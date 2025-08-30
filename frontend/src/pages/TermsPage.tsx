import React from 'react';
import { Link } from 'react-router-dom';

const TermsPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-slate-900 mb-4">Terms &amp; Conditions</h1>
      <p className="text-slate-600 mb-6">
        These Terms and Conditions ("Terms") govern your access and use of Joborra’s platform (the "Service"). By accessing
        or using our platform, you agree to be bound by these Terms.
      </p>

      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-xl font-semibold mb-2">1. User Eligibility</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>At least 18 years of age</li>
            <li>
              A valid international student, have a valid Australian VISA (Subclass 500/485), or employer legally operating in
              Australia
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">2. Joborra’s Role</h2>
          <p>
            Joborra is a digital platform that connects international students with VISA Subclass 500 and graduates with VISA
            Subclass 485 with job opportunities in Australia. We do not employ users or guarantee job placements or visa
            outcomes.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">3. Student Responsibilities</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Provide accurate and truthful information in your profile</li>
            <li>Ensure your own visa compliance and check eligibility before applying</li>
            <li>You acknowledge that Joborra is not responsible for your immigration or employment status</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">4. Employer Responsibilities</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Post only legitimate, lawful job opportunities</li>
            <li>
              Ensure roles are compliant with Australian workplace and immigration laws. Joborra will have up-to-date VISA
              compliance guide on Employer Portal for assistance.
            </li>
            <li>Not discriminate based on race, nationality, gender, visa status, or religion</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">5. Prohibited Conduct</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Post false or misleading information</li>
            <li>Impersonate others or misrepresent your identity</li>
            <li>Attempt to breach the security of our system</li>
            <li>Use Joborra for unlawful purposes</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">6. Termination</h2>
          <p>
            We reserve the right to suspend or terminate access if you breach these terms, misuse the platform, or compromise
            user trust or safety.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">7. Liability Disclaimer</h2>
          <ul className="list-disc ml-6 space-y-1">
            <li>Joborra is not responsible for visa compliance of users</li>
            <li>The accuracy of job listings or user-submitted data</li>
            <li>Employment outcomes or disputes between users</li>
          </ul>
          <p className="mt-2">
            To the maximum extent permitted by law, Joborra disclaims all liability arising from use of the Service.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">8. Intellectual Property</h2>
          <p>
            All Joborra branding, software, and content is owned by Joborra Pty Ltd. You may not reproduce, modify, or
            distribute any part without permission.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">9. Changes to Terms</h2>
          <p>
            We reserve the right to update these Terms. Continued use after changes constitutes acceptance.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-2">10. Governing Law</h2>
          <p>These Terms are governed by the laws of New South Wales, Australia.</p>
        </section>
      </div>

      <div className="mt-8">
        <Link to="/auth?tab=login" className="text-primary-600 hover:text-primary-500">Back to Sign In</Link>
      </div>
    </div>
  );
};

export default TermsPage;
