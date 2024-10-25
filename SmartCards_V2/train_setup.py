import random
random.seed(57)

def sm2(ease_factor, repetitions, interval, difficulty_score):
    # Adjust ease factor based on the difficulty score
    if difficulty_score < 3:
        ease_factor += 0.1 * (3 - difficulty_score)  # Higher ease if score is low (easy)
    elif difficulty_score > 3:
        ease_factor -= 0.1 * (difficulty_score - 3)  # Lower ease if score is high (difficult)
    
    # Ensure the ease factor stays above a minimum value to avoid too-short intervals
    ease_factor = max(1.3, ease_factor)

    # Determine the next interval based on repetitions
    if repetitions == 0:
        interval = 1  # First review is the next day
    elif repetitions == 1:
        interval = 6  # Second review after six days
    else:
        interval = round(interval * ease_factor)  # Future reviews based on ease factor

    return interval, ease_factor

def generate_synthetic_data(num_cards=1000):
    data = []
    for _ in range(num_cards):
        ease_factor = 1.1  # Starting ease factor
        interval = 0       # Initial interval before any review
        review_count = 0
        time_since_last_review = 0
        success_rate = 0
        char_count = random.randint(1, 100)  # Simulate text length in the card
        
        total_quality = 0  # For calculating average quality over time

        for review_session in range(5):  # Simulate 5 review sessions per card
            difficulty_score = random.randint(1, 5)
            
            # Calculate next interval and update ease factor using SM-2
            interval, ease_factor = sm2(ease_factor, review_count, interval, difficulty_score)
            
            # Increment review count
            review_count += 1
            
            # Update time since last review (simulate days since last review)
            time_since_last_review += interval
            
            # Simulate response time (e.g., random within a plausible range)
            last_response_time = random.uniform(0.5, 5.0)  # in seconds
            
            # Update average quality based on difficulty score
            total_quality += 5 - difficulty_score  # Higher difficulty means lower quality
            average_quality = total_quality / review_count
            
            # Update success rate as proportion of successful recalls (difficulty <= 3)
            successful_recalls = 1 if difficulty_score <= 3 else 0
            success_rate = (success_rate * (review_count - 1) + successful_recalls) / review_count
            
            # Features for each review
            features = [
                time_since_last_review,
                interval,
                review_count,
                average_quality,
                ease_factor,
                last_response_time,
                success_rate,
                char_count
            ]

            
            for i in range(len(features)):
                features[i] = round(features[i], 3)

            label = interval  # Predict interval as the label for training
            
            # Append data for this session
            data.append({"features": features, "label": label})
    
    return data

print(generate_synthetic_data())