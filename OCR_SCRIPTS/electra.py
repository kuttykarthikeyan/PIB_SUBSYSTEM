import torch
from transformers import AutoTokenizer, ElectraForSequenceClassification
from torch.utils.data import DataLoader, Dataset
from transformers import AdamW

# Define your dataset class
class MyDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.encodings = tokenizer(texts, truncation=True, padding='max_length', max_length=max_length, return_tensors='pt')
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {key: val[idx] for key, val in self.encodings.items()}, self.labels[idx]

# Load the pre-trained model and tokenizer
model_name = "bhadresh-savani/electra-base-emotion"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = ElectraForSequenceClassification.from_pretrained(model_name)

# Prepare your data (replace with your own dataset loading code)
texts = ["Hello, my dog is cute", ...]
labels = [0, ...]

# Define your dataset and data loader
max_length = 128  # You can adjust this based on your dataset and hardware constraints
dataset = MyDataset(texts, labels, tokenizer, max_length)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Define optimizer and loss function
optimizer = AdamW(model.parameters(), lr=1e-5)  # You can adjust the learning rate
loss_fn = torch.nn.CrossEntropyLoss()

# Training loop
num_epochs = 3  # You can adjust this
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

for epoch in range(num_epochs):
    model.train()
    total_loss = 0.0
    for batch in dataloader:
        inputs, targets = batch
        inputs = {k: v.to(device) for k, v in inputs}
        targets = targets.to(device)

        optimizer.zero_grad()
        outputs = model(**inputs)
        logits = outputs.logits
        loss = loss_fn(logits, targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"Epoch {epoch+1}, Loss: {total_loss / len(dataloader)}")

# Save the fine-tuned model
model.save_pretrained("fine_tuned_model")
tokenizer.save_pretrained("fine_tuned_model")




"""
from transformers import AutoTokenizer, ElectraForSequenceClassification

model_name = "fine_tuned_model"  # Replace with the path to your saved model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = ElectraForSequenceClassification.from_pretrained(model_name)


text = "This is a new text you want to classify."

# Tokenize the input text
inputs = tokenizer(text, return_tensors="pt")

# Get the model's prediction
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits

# You can then get the predicted class ID and label using the logits
predicted_class_id = logits.argmax().item()
predicted_label = model.config.id2label[predicted_class_id]

print(f"Predicted Class ID: {predicted_class_id}")
print(f"Predicted Label: {predicted_label}")


"""

