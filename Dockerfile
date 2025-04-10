# Gunakan image yang sudah punya Python dan Node.js
FROM node:18-bullseye

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy file project ke dalam container
COPY . .

# Install dependensi Node.js
RUN npm install

# Install dependensi Python
RUN pip3 install gspread oauth2client

# Jalankan bot Node.js
CMD ["node", "index.js"]
