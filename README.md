# OCS Room Booking Management Portal
A Django-based web application developed for the Office of Career Services (OCS) to efficiently manage, search, and reserve campus interview and assessment rooms.

The system provides a responsive user experience, intelligent room availability checks, conflict prevention, and a powerful custom admin dashboard for staff management.

---

# Features

## Smart Availability Search
- Search rooms dynamically based on:
  - Date
  - Time slot
  - Participant capacity

## Conflict Prevention
- Prevents double-booking automatically
- Uses:
  - Database-level locking
  - Time-overlap validation algorithms

## Role-Based Access

### Standard Users
- Search available rooms
- Create reservations
- View live room schedules

### Staff / Admin
- Access custom admin dashboard
- Manage:
  - Rooms
  - Users
  - Reservations
- Monitor all booking activity

## 🎨 Modern UI
- Built using:
  - Bootstrap 5
  - Custom CSS

---

# Tech Stack

- **Backend:** Django
- **Frontend:** HTML, CSS, Bootstrap 5
- **Database:** SQLite3
- **Language:** Python 3

---

# Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.8+
- Git

---

# Installation & Setup

Follow these steps to run the project locally.

---

## 1️.Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME