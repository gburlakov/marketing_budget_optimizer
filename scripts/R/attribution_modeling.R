# Load libraries
library(dplyr)
library(ggplot2)

# Sample data: user journeys (each list item = 1 user)
journey_data <- data.frame(
  user_id = 1:8,
  journey = I(list(
    c("Email", "Social", "Direct"),
    c("Email", "Search"),
    c("Search", "Social", "Direct"),
    c("Social", "Direct"),
    c("Email", "Social"),
    c("Direct"),
    c("Email", "Search", "Social"),
    c("Social", "Search", "Direct")
  )),
  converted = c(1, 0, 1, 1, 0, 1, 0, 1)
)

# Extract only journeys that led to a conversion
converted_paths <- journey_data %>%
  filter(converted == 1) %>%
  pull(journey)

# Create transition pairs (start -> channel -> ... -> conversion)
transitions <- do.call(rbind, lapply(converted_paths, function(path) {
  steps <- c("start", path, "conversion")
  data.frame(from = head(steps, -1), to = tail(steps, -1))
}))

# Count transitions
transition_df <- transitions %>%
  group_by(from, to) %>%
  summarise(count = n(), .groups = "drop")

# Get all unique states (channels + start/conversion)
channels_all <- unique(c(transition_df$from, transition_df$to))

# Initialize transition matrix
transition_matrix <- matrix(0, nrow = length(channels_all), ncol = length(channels_all),
                            dimnames = list(channels_all, channels_all))

# Fill matrix with transition counts
for (i in 1:nrow(transition_df)) {
  transition_matrix[transition_df$from[i], transition_df$to[i]] <- transition_df$count[i]
}

# Normalize rows to get transition probabilities
transition_matrix <- sweep(transition_matrix, 1, rowSums(transition_matrix), FUN = "/")

# transition_matrix <- matrix(c(
#   # Direct, Email, Search, Social, start, conversion
#   0.0, 0.0, 0.0, 0.0, 0.0, 1.0,  # Direct
#   0.0, 0.0, 0.0, 1.0, 0.0, 0.0,  # Email
#   0.5, 0.0, 0.0, 0.5, 0.0, 0.0,  # Search
#   0.75, 0.0, 0.25, 0.0, 0.0, 0.0,  # Social
#   0.2, 0.2, 0.2, 0.4, 0.0, 0.0,  # start
#   0.0, 0.0, 0.0, 0.0, 0.0, 1.0   # conversion
# ), nrow = 6, byrow = TRUE)
# 
# rownames(transition_matrix) <- c("Direct", "Email", "Search", "Social", "start", "conversion")
# colnames(transition_matrix) <- c("Direct", "Email", "Search", "Social", "start", "conversion")

# Safe absorption probability function
absorption_prob <- function(matrix, start = "start", end = "conversion", steps = 100) {
  if (!(start %in% rownames(matrix)) || !(end %in% colnames(matrix))) return(NA)
  
  prob <- rep(0, nrow(matrix))
  names(prob) <- rownames(matrix)
  prob[start] <- 1
  
  for (i in 1:steps) {
    prob <- prob %*% matrix
    if (any(is.nan(prob)) || all(is.na(prob))) return(NA)
  }
  
  return(prob[end])
}

# Check if there are any rows with missing values (NA) in the transition matrix
row_sums <- rowSums(transition_matrix, na.rm = TRUE)

# Check for missing row sums (if NA present in row sums)
if (any(is.na(row_sums))) {
  print("There are rows with missing values (NA)!")
  # Optionally, handle missing values here (e.g., by filling with 0 or uniform distribution)
}

# Now, check if any row sums are zero (no outgoing transitions)
if (any(row_sums == 0, na.rm = TRUE)) {
  print("There are rows with no transitions!")
  # Handle by setting transition probabilities for these rows, for example, uniform distribution
  transition_matrix[row_sums == 0, ] <- 1 / ncol(transition_matrix)  # Uniform distribution for rows with no transitions
}

# Print the row sums for debugging
print(row_sums)

# Function to calculate absorption probability
absorption_prob <- function(transition_matrix) {
  # Ensure transition_matrix is square
  if (nrow(transition_matrix) != ncol(transition_matrix)) {
    stop("Transition matrix must be square!")
  }
  
  # Identify absorbing states (states with no outgoing transitions)
  absorbing_states <- which(rowSums(transition_matrix == 0) == 0)
  
  # If there are no transient states, return 0
  if (length(absorbing_states) == nrow(transition_matrix)) {
    return(1)  # If all states are absorbing, the probability is 1
  }
  
  transient_states <- setdiff(1:nrow(transition_matrix), absorbing_states)
  
  # If there are no transient states, the absorption probability is trivially 1
  if (length(transient_states) == 0) {
    return(1)
  }
  
  # Create a submatrix for transient states (Q) and for the transitions to absorbing states (R)
  Q <- transition_matrix[transient_states, transient_states]
  R <- transition_matrix[transient_states, absorbing_states]
  
  # Create the identity matrix for the Q matrix
  I <- diag(nrow(Q))
  
  # Calculate (I - Q) inverse
  inv_I_minus_Q <- tryCatch({
    solve(I - Q)
  }, error = function(e) {
    stop("Error in solving (I - Q) inverse. Check your transition matrix.")
  })
  
  # Calculate the absorption probabilities (R * (I - Q)^(-1))
  absorption_probs <- inv_I_minus_Q %*% R
  
  # Return the absorption probabilities for transient states
  return(absorption_probs)
}

# Calculate the absorption probabilities
baseline_prob <- absorption_prob(transition_matrix)
print(paste("Baseline Conversion Probability:", baseline_prob))

# Assume the first element corresponds to the starting state
baseline_prob_start <- baseline_prob[1]

# Filter only the real touchpoint channels (exclude 'start' and 'conversion')
touchpoint_channels <- setdiff(channels_all, c("start", "conversion"))

# Attribution via removal effect
removal_effect <- sapply(touchpoint_channels, function(channel) {
  temp_matrix <- transition_matrix
  
  # Zero out transitions to and from the channel
  temp_matrix[channel, ] <- 0
  temp_matrix[, channel] <- 0
  
  # For each row, fix zero-row issues by redistributing probability
  for (i in 1:nrow(temp_matrix)) {
    row_sum <- sum(temp_matrix[i, ])
    
    if (row_sum == 0) {
      # Valid columns = all except the current row and the removed channel
      valid_cols <- setdiff(colnames(temp_matrix), c(channel, rownames(temp_matrix)[i]))
      if (length(valid_cols) > 0) {
        temp_matrix[i, valid_cols] <- 1 / length(valid_cols)
      }
    } else {
      # Normalize the row to sum to 1
      temp_matrix[i, ] <- temp_matrix[i, ] / row_sum
    }
  }
  print(temp_matrix)

  
  # Compute probability after removing and rebalancing
  removed_prob <- tryCatch({
    prob <- absorption_prob(temp_matrix)
    prob[1]  # probability from start
  }, error = function(e) {
    warning(paste("Error when removing", channel, ":", e$message))
    return(NA)
  })
  
  print(paste("Probability without", channel, ":", removed_prob))
  
  if (is.na(removed_prob)) return(0)
  return(baseline_prob_start - removed_prob)
})


# Show the result
print(removal_effect)

# Normalize to get attribution scores (only if the sum is positive)
if (sum(removal_effect, na.rm = TRUE) > 0) {
  attribution <- removal_effect / sum(removal_effect, na.rm = TRUE)
} else {
  attribution <- setNames(rep(0, length(removal_effect)), names(removal_effect))
}

# Format attribution data
attribution_df <- data.frame(
  channel = names(attribution),
  score = as.numeric(attribution)
)

# Print final attribution scores
print(attribution_df)