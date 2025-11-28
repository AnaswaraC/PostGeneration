
```markdown
# 🌌 Pollyn Frontend — Angular Dashboard

This is the **frontend dashboard** for **Pollyn**, an interactive Angular web application featuring a glassmorphic interface, smooth scrolling navigation, 3D visual effects, and modal-based authentication.

---

## 🚀 Features

- ⚡ **Angular 15** SPA (Single Page Application)
- 🧊 **Glassmorphic UI** with floating navigation
- 🔄 **Smooth scroll navigation** between page sections
- 🧭 **Dynamic nav indicator** tracking active sections
- 👤 **Login / Signup / Profile modals** with scroll lock
- 🌀 **3D rotating card history** and scrollable discovery feed
- 🌗 **Responsive layout** optimized for desktop & tablet
- 🛠️ Built with **PrimeIcons**, **SCSS**, and Angular animations

---

## 🧱 Project Structure

```

src/
├── app/
│    ├── dashboard/
│    │     ├── dashboard.component.ts
│    │     ├── dashboard.component.html
│    │     ├── dashboard.component.scss
│    │
│    ├── components/
│    │     ├── create-post/
│    │     ├── history/
│    │     ├── discover/
│    │     └── footer/
│    │
│    ├── services/
│    └── app.module.ts
│
├── assets/
│    └── natural.svg
│
├── styles.scss
└── index.html

````

---

## 🧩 Key Components

| Component | Description |
|------------|--------------|
| **Dashboard** | Main layout with navbar and scroll-tracking sections |
| **Create Post** | AI-assisted post generator |
| **History** | 3D spinning card carousel showing generated posts |
| **Discover** | Scrollable vertical feed of community content |
| **Footer** | Dynamic footer section with glassmorphic styling |
| **Auth Modals** | Login, Signup, and Profile pop-ups with scroll lock |

---

## 🖥️ Development Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/pollyn-frontend.git
cd pollyn-frontend
````

### 2️⃣ Install dependencies

```bash
npm install
```

### 3️⃣ Run the development server

```bash
ng serve
```

Open your browser and navigate to **[http://localhost:4200/](http://localhost:4200/)**.

Angular will automatically reload whenever you modify a source file.

---

## 🏗️ Build

To build the production-ready app:

```bash
ng build
```

The optimized output will be stored in the `dist/` folder.

---

## 🧪 Testing

### Unit Tests

```bash
ng test
```

### End-to-End Tests

```bash
ng e2e
```

> Note: You must install a compatible E2E framework such as Cypress or Protractor before running E2E tests.

---

## 🧠 Development Notes

* Navigation uses **smooth scroll with section offset tracking**.
* The app **locks scrolling until login/signup** to protect content.
* The **indicator automatically updates** when scrolling through sections.
* Built with a **modular architecture**, so you can easily extend sections or add more routes.

---

## 🧾 Tech Stack

| Technology     | Purpose                                  |
| -------------- | ---------------------------------------- |
| **Angular 15** | Frontend framework                       |
| **SCSS**       | Styling and glassmorphism effects        |
| **PrimeIcons** | Icons used in navbar and UI elements     |
| **TypeScript** | Strongly-typed logic & DOM interaction   |
| **Renderer2**  | Dynamic style updates for nav animations |

---

## 🌐 Deployment

You can deploy the built `dist/` folder on any static host:

* GitHub Pages
* Netlify
* Vercel
* Firebase Hosting
* AWS Amplify

Example (GitHub Pages):

```bash
ng build --output-path docs --base-href /pollyn-frontend/
```
