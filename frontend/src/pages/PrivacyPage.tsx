import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-slate-900 mb-4">Privacy Policy</h1>
      <p className="text-slate-600 mb-6">
        Joborra Pty Ltd ("Joborra", "we", "us", or "our") is committed to protecting your privacy. This Privacy Policy
        explains how we collect, use, disclose, and protect your personal information in accordance with the Australian
        Privacy Act 1988 (Cth) and the Australian Privacy Principles (APPs).
      </p>

      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-xl font-semibold mb-2">1. What Information We Collect</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Full name, contact details (email, phone), Date of Birth</li>
            <li>Resume or employment history</li>
            <li>Visa status and work eligibility information (including via VEVO)</li>
            <li>Employer business and contact information</li>
            <li>Job listing and application data</li>
            <li>Optional: feedback, preferences, IP address, analytics (via cookies)</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">2. How We Collect Your Information</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Create an account or submit a form</li>
            <li>Post or apply to a job</li>
            <li>Contact us via email or support</li>
            <li>Use our platform (automated tracking for security/analytics)</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">3. Why We Collect Your Information</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Provide and maintain our platform</li>
            <li>
              Match compliant international students on VISA Subclass 500 or users on VISA Subclass 485 with compliant job
              opportunities
            </li>
            <li>Facilitate communication between candidates and employers</li>
            <li>Improve our services and ensure legal compliance</li>
            <li>Comply with applicable laws and regulations</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">4. How We Store and Secure Your Information</h2>
          <p>
            We store data securely using reputable cloud services. We implement access controls, encryption, and regular audits
            to prevent unauthorized access or misuse.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">5. Disclosure to Third Parties</h2>
          <p className="mb-2">We may disclose your personal information to:</p>
          <ul className="list-disc ml-6 space-y-1">
            <li>Service providers who assist us (e.g., Airtable, email services)</li>
            <li>Regulatory or legal authorities as required by law</li>
          </ul>
          <p className="mt-2">We do not sell or rent your personal data.</p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">6. Overseas Disclosure</h2>
          <p>
            Your data may be stored or processed in overseas locations where our service providers operate. We take reasonable
            steps to ensure such entities comply with Australian privacy standards.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">7. Access &amp; Correction</h2>
          <p>
            You may access, update, or correct your personal information at any time by logging into your account or
            contacting us at <a className="text-primary-600" href="mailto:Manav@Joborra.com">Manav@Joborra.com</a>.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">8. Deletion of Information</h2>
          <p>
            You may request deletion of your data by contacting us. We will comply unless we are legally obligated to retain it.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">9. Cookies &amp; Analytics</h2>
          <p>
            Our website uses cookies for functionality and analytics. By using the site, you consent to the use of cookies in
            accordance with this policy.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">10. Contact Us</h2>
          <p className="mb-2">If you have any privacy concerns or complaints, please contact:</p>
          <p>Privacy Officer – Joborra Pty Ltd</p>
          <p>
            Email: <a className="text-primary-600" href="mailto:Manav@Joborra.com">Manav@Joborra.com</a>
          </p>
          <p>We aim to respond within 30 days of receiving your complaint.</p>
        </section>
      </div>

      <div className="mt-8">
        <Link to="/auth?tab=login" className="text-primary-600 hover:text-primary-500">Back to Sign In</Link>
      </div>
    </div>
  );
};

export default PrivacyPage;
