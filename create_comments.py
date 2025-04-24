# ====== Import the required modules
import random
import csv
from datetime import datetime, timedelta
import ulid  # For generating ULIDs
from faker import Faker  # For generating fake names

# Initialize Faker for generating fake names
fake = Faker()

# ====== Function to generate ULID-based customer identifier
def generate_customer_number():
    return ulid.new().str  # Generates a sortable ULID as a string

# ====== Function to generate random order number (up to 5 digits)
def generate_order_number():
    return random.randint(1, 99999)

# ====== Function to generate random date in 2025 up to April 10
def generate_order_date():
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 4, 10)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

# ====== Function to generate mock customer response based on an NPS score
def generate_customer_response(nps_score):
    # Expanded topics dictionary with more realistic sporting goods store complaints
    topics = {
        1: [
            "Outstanding customer service, staff went above and beyond to help me find the right gear.",
            "Best prices I’ve seen for high-quality fishing rods, no complaints here!",
            "Product was in stock and worked perfectly, couldn’t be happier.",
            "Fast shipping on my online order, arrived ahead of schedule.",
            "Return process was super easy and hassle-free.",
            "Knowledgeable staff helped me pick the perfect hunting boots."
        ],
        2: [
            "Good pricing on camping gear, but the checkout line took forever.",
            "Reliable product, though the staff seemed too busy to assist.",
            "Decent selection, but I wish they had more sizes in stock.",
            "Customer service was friendly but not very knowledgeable about firearms.",
            "Business hours are convenient, but the store was a bit messy.",
            "Online order arrived on time, but packaging was slightly damaged."
        ],
        3: [
            "Average experience, pricing was okay but nothing special.",
            "Product availability was hit or miss, had to settle for my second choice.",
            "Customer service was fine but didn’t seem to care much.",
            "Store was clean, but the return policy felt restrictive.",
            "Shipping took longer than expected for my kayak order.",
            "Business hours are alright, but they close too early on weekends."
        ],
        4: [
            "Poor product availability, they were out of the tent I wanted.",
            "Hidden fees popped up at checkout, really soured the experience.",
            "Customer service was slow and unhelpful with my warranty question.",
            "Unreliable product—my reel broke after one fishing trip.",
            "Store hours are inconvenient, closed when I needed to shop.",
            "Online order was delayed with no updates, frustrating process."
        ],
        5: [
            "Terrible customer service, staff ignored me while I waited for help.",
            "Hidden fees everywhere, felt like a bait-and-switch on pricing.",
            "Product was defective—my bike tire popped on the first ride.",
            "Return policy is a nightmare, they wouldn’t take back a faulty item.",
            "Out of stock on half the fishing gear I needed, waste of a trip.",
            "Business hours are ridiculous, closed mid-day when I stopped by.",
            "Online order lost in transit and no one could explain why."
        ]
    }
    # Randomly select 1-3 topics based on NPS score
    num_issues = random.randint(1, 3)
    selected_topics = random.sample(topics[nps_score], min(num_issues, len(topics[nps_score])))
    return " and ".join(selected_topics) + "."

# ====== Generate 205 randomly populated rows of customer comments
data = []
for _ in range(205):
    nps_score = random.randint(1, 5)
    row = [
        generate_customer_number(),
        fake.first_name(),  # Generate fake first name
        fake.last_name(),   # Generate fake last name
        generate_order_number(),
        generate_order_date(),
        nps_score,
        generate_customer_response(nps_score)
    ]
    data.append(row)

# ====== Write the data to a CSV
with open('nps_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Customer Number', 'First Name', 'Last Name', 'Order Number', 'Order Date', 'NPS Score', 'Customer Response'])
    writer.writerows(data)

print("CSV file 'nps_data.csv' has been generated.")