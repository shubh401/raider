# Copyright (C) 2024 Shubham Agarwal, CISPA.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


FROM alpine:latest

# Install necessary packages
RUN apk add --no-cache \
    bash \
    curl \
    gcc \
    g++ \
    make \
    python3 \
    python3-dev \
    py3-pip \
    nodejs \
    npm

# Set the working directory
WORKDIR /usr/src/app

# Install NPM dependencies
RUN npm install --save unzip-crx-3 escodegen fs-extra acorn acorn-loose

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# Copy the static analyzer
COPY . .

# Entrypoint
CMD ["python", "processor.py"]
