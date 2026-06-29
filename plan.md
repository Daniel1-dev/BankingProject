# Plan: Modernizing Registration and Adding Features

The user wants to transform the registration process into a multi-step, OPay-inspired flow, add more profile fields (gender, image), and implement new features (Airtime, Data, Bills) along with a light/dark mode toggle.

## Phase 1: Update Database Models
- Add `gender` and update profile fields in `models.py`.
- Run migrations.

## Phase 2: Refactor Registration Form
- Replace the current long registration page with a multi-step flow using Alpine.js or vanilla JS for sections (e.g., "Account Info", "Personal Details", "Security").
- Update `register` view in `views.py` to handle data across steps or just process it all at once via a cleaner JS-driven UI.

## Phase 3: Add New Features (Airtime/Data/Bills)
- Create new templates for these services.
- Implement logic in `views.py` to mock or simulate these API interactions (using standard Django patterns).

## Phase 4: Theme Customization (Light/Dark Mode)
- Implement a simple Tailwind CSS theme toggle (e.g., class on `body` tag) stored in `localStorage` or user session.

## Phase 5: Profile Updates
- Ensure `ProfileUpdateForm` allows profile picture uploads.
- Add an "Update Profile" section in the user dashboard.

---
I will start by updating the models and then the registration UI.
EOF
