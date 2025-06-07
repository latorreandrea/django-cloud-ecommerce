# BluntTee – Cloud-Native E-commerce Platform

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
  - [System Overview](#system-overview)
  - [Database ER Diagram](#database-er-diagram)
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
- [Next Steps](#next-steps)

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
- **Manual Product Updates:** Admin users can update products from Shirtigo by accessing the URL `/products/admin/update-products/` after login, ensuring newly created or modified products are synchronized with the app.
- **Modern Stack:** Uses Django, PostgreSQL (Neon), and modern frontend practices.


The website has the following features available to different types of users:

Feature	Not logged in	Logged in as regular user	Logged in as admin
Home Page	✅	✅	✅
Products			
Products Listing	✅	✅	✅
Product Detail	✅	✅	✅
Cart & Wishlist			
View Cart	✅	✅	✅
Add to Cart	✅	✅	✅
View Wishlist	❌	✅	✅
Add to Wishlist	❌	✅	✅
Checkout			
Checkout Process	✅	✅	✅
View Order Confirmation	✅	✅	✅
User Features			
My Profile	❌	✅	✅
Order History	❌	✅	✅
View Order Shipping Status	❌	✅	✅
Register	✅	❌	❌
Login	✅	❌	❌
Logout	❌	✅	✅
Admin Features			
Update Products from Shirtigo	❌	❌	✅
Django Admin Interface	❌	❌	✅
View Order Management	❌	❌	✅
Update Site Content	❌	❌	✅

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

### Database ER Diagram

Below is a simplified Entity-Relationship (ER) schema of the main models:

```
+-------------------+         +-------------------+         +-------------------+
|     User          |         |   UserProfile     |         |     Product       |
|-------------------|         |------------------|         |-------------------|
| id (BigAutoField) PK        | id (BigAutoField) PK        | id (BigAutoField) PK
| username (str)              | user (OneToOne)   FK->User  | name (str)
| email (str)                 | full_name (str)             | shirtigo_id (int)
| ...                         | contact_email (str)         | category (FK)      FK->Category
                              | phone_number (str)          | description (text)
                              | country (str)               | price (decimal)
                              | ...                         | cost (decimal)
                                                            | colors (M2M)       FK->Color
                                                            | sizes (M2M)        FK->Size

+-------------------+         +-------------------+         +-------------------+
|    Category       |         |      Color        |         |      Size         |
|-------------------|         |------------------|         |-------------------|
| id (BigAutoField) PK        | id (BigAutoField) PK        | id (BigAutoField) PK
| name (str)                  | name (str)                  | name (str)
| friendly_name (str)         | shirtigo_color_id (int)     | shirtigo_size_id (int)
| material_care (text)        |                             |

+-------------------+         +-------------------+         +-------------------+
|   ProductImage    |         |      Cart         |         |    CartItem       |
|-------------------|         |------------------|         |-------------------|
| id (BigAutoField) PK        | id (BigAutoField) PK        | id (BigAutoField) PK
| product (FK)      FK->Product| user (OneToOne)  FK->User  | cart (FK)         FK->Cart
| color (FK)        FK->Color |                          | product (FK)      FK->Product
| small_image (url)           |                          | color (FK)        FK->Color
| large_image (url)           |                          | size (FK)         FK->Size
                                                            | quantity (int)

+-------------------+         +-------------------+         +-------------------+
|     Wishlist      |         |   WishlistItem    |         |      Order        |
|-------------------|         |------------------|         |-------------------|
| id (BigAutoField) PK        | id (BigAutoField) PK        | id (BigAutoField) PK
| user (OneToOne)   FK->User  | wishlist (FK)     FK->Wishlist| user (FK)        FK->User
                              | product (FK)      FK->Product | status (str)
                              | added_at (datetime)           | created_at (datetime)
                                                            | paid (bool)
                                                            | ... (shipping/billing fields)

+-------------------+         +-------------------+         +-------------------+
|    OrderItem      |         |   ShirtigoOrder   |         |  ShirtigoAPILog   |
|-------------------|         |------------------|         |-------------------|
| id (BigAutoField) PK        | id (BigAutoField) PK        | id (BigAutoField) PK
| order (FK)        FK->Order | order (OneToOne)  FK->Order | shirtigo_order (FK) FK->ShirtigoOrder
| product (FK)      FK->Product| shirtigo_order_id (str)    | request_data (JSON)
| quantity (int)              | status (str)                | response_data (JSON)
| price (decimal)             | status_message (text)       | success (bool)
| color (FK)        FK->Color | created_at (datetime)       | timestamp (datetime)
| size (FK)         FK->Size  | updated_at (datetime)       | endpoint (str)

+-------------------+         +-------------------+         +-------------------+
|    EventLog       |         |   PendingOrder    |
|-------------------|         |------------------|
| id (BigAutoField) PK        | id (BigAutoField) PK
| stripe_id (str)              | order_data (JSON)
| event_type (str)             | items_data (JSON)
| processed_at (datetime)      | stripe_payment_intent (str)
                               | created_at (datetime)
                               | expires_at (datetime)
```

**Legend:**  
- `PK` = Primary Key  
- `FK` = Foreign Key (→ referenced table)  
- `M2M` = Many-to-Many relationship

> *Note: Only main fields and relationships are shown for clarity. Some auxiliary fields (timestamps, status, etc.) are omitted.*

---


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

## Next Steps

- **Marketing implementation:**
  Add a marketing app
- **Expand Payment Methods:**  
  Integrate additional payment gateways for broader customer reach.
- **Analytics and Reporting:**  
  Add dashboards for sales analytics and product performance.
- **Internationalization:**  
  Support multiple languages and currencies.
- **Performance Optimization:**  
  Implement caching and optimize database queries for scalability.
- **User Reviews and Ratings:**  
  Allow customers to leave feedback on products.
- **Marketing Integrations:**  
  Integrate with email marketing and social media platforms.


**BluntTee** – Cloud-Native E-commerce Example  
Built with Django & Google Cloud by Andrea Latorre