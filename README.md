Abhey Tiwari - Personal Portfolio Website
This repository contains the source code for Abhey Tiwari's personal portfolio website, designed to showcase his expertise as a Software Engineer specializing in AI & Web Development. The website features a clean, modern design with interactive elements and is fully responsive across various devices.

Features
Responsive Design: Adapts seamlessly to desktop, tablet, and mobile screens.

Animated Hero Section: Dynamic typing effect for name and profession.

Skills Section: Dedicated section displaying technical skills efficiently with categorized cards.

Project Showcase: Grid layout for highlighting key projects.

Contact Form: A simple, design-only contact form for inquiries.

Resume Download: A prominent button to download the latest resume.

Smooth Scrolling Navigation: Intuitive navigation between sections with active link highlighting.

Translucent Navbar: Modern, frosted-glass effect for the fixed navigation bar.

SEO Optimized: Includes meta tags for better search engine visibility and social media sharing.

Technologies Used
HTML5: For structuring the web content.

CSS3: For styling and animations, including a custom dark theme.

JavaScript (ES6+): For interactive elements, animations, and dynamic content.

Font Awesome: Used for icons (e.g., download, social media).

Google Fonts: For modern and professional typography (Montserrat, Roboto).

Setup and Installation
To get a local copy up and running, follow these simple steps:

Clone the repository:

git clone https://github.com/yourusername/your-portfolio-repo.git

(Replace yourusername/your-portfolio-repo with your actual GitHub repository link.)

Navigate to the project directory:

cd your-portfolio-repo

Open index.html:
Simply open the index.html file in your preferred web browser.

Alternatively, you can use a local server (e.g., Live Server VS Code extension) for a better development experience.

Customization
You can easily customize the content of this portfolio to make it your own:

Personal Information (index.html):

Name and Title: Update the <title> tag in the <head> and the names array in the <script> block for the typing animation.

About Me Description: Edit the paragraphs within the <div class="profile-bio"> to reflect your background and aspirations.

Contact Information: Update email in the footer mailto: link.

Social Media Links: Modify the href attributes in the footer .social-icons section with your LinkedIn, GitHub, and other profiles.

Profile Image (index.html):

Replace https://placehold.co/600x800/1a1a1a/f0f0f0?text=Your+Image+Here with the URL to your actual professional profile image. It's recommended to host your image and use its direct URL.

Resume Download Link (index.html):

Locate the <a> tag with class="btn btn-download-resume".

Change href="resume 3.pdf" to the correct path and filename of your resume. Ensure your resume PDF file is in the same directory as index.html or provide the correct relative/absolute path.

You can also update the download attribute to change the default downloaded filename (e.g., download="YourName_Resume.pdf").

Skills Section (index.html):

Edit the <li> items within each <div class="skill-category"> to list your specific languages, frameworks, AI/ML concepts, web dev skills, and tools.

Projects Section (index.html):

Modify the <h3> and <p> tags within each <div class="project-card"> to describe your projects.

Update the href attribute of the <a> tags with class="project-link" to link to your project repositories or live demos.

SEO & Open Graph Tags (index.html - in <head>):

Update meta name="description" and meta name="keywords" for better search engine optimization.

Crucially, update meta property="og:image" and meta property="og:url" with your specific website image and URL for accurate social media previews when shared.

Usage / Deployment
Since this is a static HTML website, deployment is straightforward:

GitHub Pages: Push your code to a GitHub repository, then enable GitHub Pages in your repository settings. This provides a free, easy way to host your portfolio online.

Any Static Hosting Service: Upload the index.html file (and any associated assets if you were to split CSS/JS back out) to a service like Netlify, Vercel, or Firebase Hosting.

Contact
Feel free to connect with me!

Email: abheytiwarikvs@gmail.com

LinkedIn: Your LinkedIn Profile

GitHub: Your GitHub Profile

License
This project is open-source and available under the MIT License. (Consider creating a LICENSE file in your repository if you choose a license).
