# BluntTee – Cloud-Native E-commerce Platform

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
  - [System Overview](#system-overview)
  - [Technology Stack](#technology-stack)
  - [Data Flow](#data-flow)
- [Setup & Installation](#setup--installation)
- [Deployment](#deployment)
- [Integrations](#integrations)
- [Usage](#usage)
- [Testing](#testing)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Project Overview

**BluntTee** is a demonstration e-commerce platform built with Django and deployed on Google Cloud.  
Its main goal is to showcase technical skills in designing, integrating, and deploying a modern, cloud-native e-commerce solution.  
The platform allows the BluntTee team to create and manage products via the Shirtigo Cockpit (Print-on-Demand), synchronize them with the web app, and sell them to customers with real payment and order fulfillment.

---

## Features

- **Cloud-Native Deployment:** Runs on Google Cloud Run with CI/CD via Google Cloud Build.
- **Product Management:** Products are created and managed on Shirtigo Cockpit and synchronized to the web app.
- **Customer Experience:** Customers can browse products, register, manage wishlists, and view order history.
- **Secure Payments:** Stripe integration for real payment processing.
- **Automated Emails:** Transactional emails (registration, order confirmation, etc.) via Zoho Mail.
- **Order Fulfillment:** Orders are automatically placed on Shirtigo after successful payment.
- **Status Sync:** Order statuses are updated from Shirtigo every two days.
- **Modern Stack:** Uses Django, PostgreSQL (Neon), and modern frontend practices.

---

## Architecture

### System Overview

The BluntTee web app is the main interface for customers, acting as a storefront for product sales.  
Product creation and management are handled externally on [Shirtigo.com](https://cockpit.shirtigo.com), a print-on-demand platform.

```
+-------------------+        +-------------------+        +-------------------+
|   Shirtigo.com    |<------>|   BluntTee Team   |<------>|   BluntTee App    |
| (Product Mgmt &   |        | (Product Creation |        | (Storefront,      |
|  Fulfillment)     |        |  & Budgeting)     |        |  Customer Portal) |
+-------------------+        +-------------------+        +-------------------+
                                                           |
                                                           v
                                                +----------------------+
                                                |   Customers          |
                                                | (Browse, Buy, Track) |
                                                +----------------------+
```

### Technology Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JS (Bootstrap)
- **Database:** PostgreSQL (Neon)
- **Cloud:** Google Cloud Run, Cloud Build, Cloud Storage, Secret Manager
- **Email:** Zoho Mail (SMTP)
- **Payments:** Stripe
- **Print-on-Demand:** Shirtigo API
- **ETL:** Custom Python scripts for product sync

### Data Flow

1. **Product Creation:**  
   The BluntTee team creates products and manages budgets on Shirtigo Cockpit.
2. **Product Sync:**  
   A pipeline (Python ETL) fetches and updates products in the app's database via the Shirtigo API.
3. **Product Display:**  
   Products become available for customers on [www.blunttee.com](https://www.blunttee.com).
4. **Customer Actions:**  
   Customers can register, manage wishlists, and view their order history.
5. **Purchase:**  
   Customers select products, sizes, and colors, then proceed to checkout.
6. **Payment:**  
   Stripe processes the payment securely.
7. **Order Placement:**  
   On successful payment, an order is created on Shirtigo via API.
8. **Order Status Updates:**  
   Every two days, the app updates order statuses from Shirtigo for pending shipments.
9. **Order History:**  
   Orders are stored and visible to registered users in their account area.

---

## Setup & Installation


## Deployment

- **Google Cloud Run:**  
  Deploy the app using Cloud Build pipelines for CI/CD.
- **Google Cloud Storage:**  
  Used for static and media files.
- **Google Cloud Secret Manager:**  
  All sensitive credentials (DB, API keys, SMTP) are managed securely.

---

## Integrations

- **Shirtigo API:**  
  For product management and order fulfillment.
- **Stripe:**  
  For secure payment processing.
- **Zoho Mail:**  
  For transactional email delivery.

---

## Usage

- **Customers:**  
  Browse products, register, add to cart, checkout, and track orders.
- **Admins:**  
  Manage products (via Shirtigo), view orders, and monitor system status.

---

## Testing


---

## Security

- All secrets are stored in Google Cloud Secret Manager.
- HTTPS enforced in production.
- Stripe handles all payment data securely.
- User data is protected via Django's authentication and permissions.

---

## Troubleshooting

- **Email issues:**  
  Ensure Zoho SMTP credentials are correct and the correct SMTP host is set (`smtp.zoho.eu` for EU accounts).
- **Product sync:**  
  Check Shirtigo API credentials and logs for ETL errors.
- **Payments:**  
  Verify Stripe keys and webhook configuration.

---

## License

This project is for demonstration purposes.

---

**BluntTee** – Cloud-Native E-commerce Example  
Built with Django & Google Cloud by Andrea Latorre