# Bookmark Manager

Bookmark Manager is a multi-user web application for managing bookmarks. It allows users to organize bookmarks into collections and categories, add notes, and assign tags. The app also supports importing bookmarks from a Netscape Bookmark file format and provides password reset functionality.

## Features

- **User Authentication**: Sign up, log in, and password reset using email.
- **Organized Bookmark Management**:
  - Collections for high-level organization.
  - Categories within collections for finer grouping.
  - Bookmarks with URLs, notes, and tags.
- **Import Bookmarks**: Supports importing bookmarks from Netscape Bookmark files.
- **Responsive Design**: Works seamlessly on desktops and mobile devices.
- **Persistent Database**: Stores data using SQLite with an option for external databases.
- **Docker Support**: Easily deployable using Docker and Docker Compose.

---


## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Docker (v20.10 or later)
- Docker Compose (v2.0 or later)

---

## Installation and Usage

### Docker Compose

```yaml
services:
  app:
    build: .
    container_name: pcdiks/bookmark_manager:latest
    environment:
      - SECRET_KEY=your-very-secret-key
      - EMAIL_HOST=smtp.example.com
      - EMAIL_PORT=587
      - EMAIL_USE_TLS=True
      - EMAIL_USE_SSL=False
      - EMAIL_HOST_USER=your-email@example.com
      - EMAIL_HOST_PASSWORD=your-email-password
      - DEFAULT_FROM_EMAIL=no-reply@example.com
      - DB_NAME=/data/db.sqlite3
    volumes:
      - ./data:/data  # Persistent storage for SQLite database
    ports:
      - "80:80"
```

License

This project is licensed under the GNU GENERAL PUBLIC LICENSE. See the LICENSE file for details.