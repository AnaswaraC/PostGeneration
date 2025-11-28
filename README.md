---

# 🌿 **Pollyn — AI-Powered Social Discovery Platform**

Pollyn is an interactive, AI-enhanced social platform that helps users create, explore, and share content in a beautifully designed, glassmorphic Angular interface.
This repository contains the **Pollyn frontend** built with **Angular 15**, featuring smooth scrolling navigation, 3D UI elements, and modal-based authentication.

> If your project contains a backend, include it here. Otherwise, this README focuses on the **frontend**.

---

# ✨ **Features**

### 🎨 **Cutting-Edge UI**

* Glassmorphic, responsive dashboard
* Floating navigation bar with active section indicators
* Smooth scrolling with intelligent section tracking
* Modern layout optimized for desktop + tablets

### 👤 **User System**

* Modal-based Login, Signup, and Profile
* Body scroll-locking during authentication
* Animated open/close transitions

### ⚙️ **Interactive Components**

* AI-powered **Create Post** module
* 3D rotating **History** carousel
* Scrollable **Discover** feed
* Modular and extensible component architecture

### 🧰 **Tech Stack**

| Technology     | Purpose                                  |
| -------------- | ---------------------------------------- |
| **Angular 15** | SPA Frontend Framework                   |
| **SCSS**       | Glassmorphism, layout, responsive styles |
| **PrimeIcons** | Iconography                              |
| **TypeScript** | Strong logic typing & DOM structure      |
| **Renderer2**  | Dynamic style + nav animations           |

---

# 📁 **Project Structure**

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
```

---

# 🚀 **Getting Started (Frontend)**

## 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/pollyn-frontend.git
cd pollyn-frontend

```

## 2️⃣ Install dependencies

```bash
npm install
```

## 3️⃣ Run the development server

```bash
ng serve
```

Navigate to **[http://localhost:4200/](http://localhost:4200/)**.
Angular automatically reloads on file changes.

---

# 🧱 **Build for Production**

```bash
ng build
```

The optimized build outputs to:

```
dist/
```

---

# 🧪 **Testing**

### Unit Tests

```bash
ng test
```

### End-to-End Tests (requires Cypress/Protractor)

```bash
ng e2e
```

# 🌐 **Deployment**

You can deploy the built `dist/` folder to any static web host:

* GitHub Pages
* Netlify
* Vercel
* Firebase Hosting
* AWS Amplify

### Example — GitHub Pages:

```bash
ng build --output-path docs --base-href /pollyn-frontend/
```
