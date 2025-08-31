import React from 'react';
import { CheckCircle, AlertCircle, Users, Shield, Globe, Heart, FileText } from 'lucide-react';

const EmployerVisaGuidePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      <main className="pt-20">
        <div className="max-w-4xl mx-auto px-4 py-12">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-slate-900 mb-4">
              Hiring International Students with Confidence
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              A comprehensive guide for employers on hiring international students legally and effectively
            </p>
          </div>

          {/* Content Sections */}
          <div className="space-y-12">
            {/* Section 1: Why This Guide */}
            <section className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <FileText className="h-8 w-8 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-4">1. Why This Guide?</h2>
                  <p className="text-slate-700 leading-relaxed">
                    Many employers hesitate to hire international students because of visa and compliance uncertainty. 
                    The truth: hiring international students is legal, simple, and beneficial — and Joborra makes it 
                    even easier by verifying every job you post.
                  </p>
                </div>
              </div>
            </section>

            {/* Section 2: Key Visa Rules */}
            <section className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <Shield className="h-8 w-8 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-6">2. Key Visa Rules (Subclass 500 Student Visa)</h2>
                  
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-3">Work Hours:</h3>
                      <ul className="space-y-2 text-slate-700">
                        <li className="flex items-start space-x-2">
                          <span className="text-primary-600 mt-1">•</span>
                          <span>During study periods → up to 48 hours per fortnight</span>
                        </li>
                        <li className="flex items-start space-x-2">
                          <span className="text-primary-600 mt-1">•</span>
                          <span>During official semester breaks → unlimited hours</span>
                        </li>
                      </ul>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-3">Type of Work:</h3>
                      <p className="text-slate-700">
                        Casual, part-time, internships, and graduate roles are permitted.
                      </p>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-3">Fair Work Protection:</h3>
                      <p className="text-slate-700">
                        Students have the same workplace rights as all other employees in Australia 
                        (minimum wage, safety, leave, superannuation).
                      </p>
                    </div>

                    <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                      <p className="text-primary-800 font-medium">
                        👉 No employer sponsorship is required for international students on a Student Visa.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 3: Common Employer Concerns */}
            <section className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-8 w-8 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-6">3. Common Employer Concerns — Answered</h2>
                  
                  <div className="space-y-6">
                    <div className="border-l-4 border-primary-200 pl-4">
                      <p className="text-slate-700 mb-2">
                        <span className="font-medium">❓ "Am I allowed to hire international students?"</span>
                      </p>
                      <p className="text-slate-700">
                        <span className="font-medium text-green-600">✅ Yes.</span> It's fully legal, provided students respect their visa work limits.
                      </p>
                    </div>

                    <div className="border-l-4 border-primary-200 pl-4">
                      <p className="text-slate-700 mb-2">
                        <span className="font-medium">❓ "What if they work too many hours?"</span>
                      </p>
                      <p className="text-slate-700">
                        <span className="font-medium text-green-600">✅ Responsibility sits with the student, not you.</span> You're not liable if they hold another job.
                      </p>
                    </div>

                    <div className="border-l-4 border-primary-200 pl-4">
                      <p className="text-slate-700 mb-2">
                        <span className="font-medium">❓ "Do I need special approvals or extra paperwork?"</span>
                      </p>
                      <p className="text-slate-700">
                        <span className="font-medium text-green-600">✅ No.</span> Hiring them is the same as hiring a domestic student (TFN, payslip, Fair Work compliance).
                      </p>
                    </div>

                    <div className="border-l-4 border-primary-200 pl-4">
                      <p className="text-slate-700 mb-2">
                        <span className="font-medium">❓ "What about internships or placements?"</span>
                      </p>
                      <div className="text-slate-700 space-y-1">
                        <p><span className="font-medium text-green-600">✅ Paid internships</span> = covered by Fair Work rules.</p>
                        <p><span className="font-medium text-green-600">✅ Unpaid placements</span> = only legal if they're a mandatory part of the student's course.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 4: How Joborra Keeps You Compliant */}
            <section className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-8 w-8 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-6">4. How Joborra Keeps You Compliant</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-2">Verified Listings:</h3>
                      <p className="text-slate-700">
                        Every role is checked against visa conditions before going live.
                      </p>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-2">Employer Guidance:</h3>
                      <p className="text-slate-700">
                        Clear prompts when you post jobs (hours, contract type, Fair Work rules).
                      </p>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-slate-800 mb-2">Resources & Support:</h3>
                      <p className="text-slate-700">
                        We keep you informed with the latest visa and workplace updates.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 5: Why Hire International Students */}
            <section className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <Users className="h-8 w-8 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-6">5. Why Hire International Students?</h2>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <Globe className="h-5 w-5 text-primary-600 mt-1 flex-shrink-0" />
                        <p className="text-slate-700">They bring global perspectives and multilingual skills.</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <Heart className="h-5 w-5 text-primary-600 mt-1 flex-shrink-0" />
                        <p className="text-slate-700">They show strong loyalty and retention.</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <Shield className="h-5 w-5 text-primary-600 mt-1 flex-shrink-0" />
                        <p className="text-slate-700">They are resilient and highly motivated, balancing study and work.</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <CheckCircle className="h-5 w-5 text-primary-600 mt-1 flex-shrink-0" />
                        <p className="text-slate-700">They are a cost-effective way to access talent — no sponsorship needed.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 6: Legal Disclaimer */}
            <section className="bg-white rounded-lg shadow-sm p-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <FileText className="h-8 w-8 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900 mb-4">6. Legal Disclaimer</h2>
                  <p className="text-slate-700 mb-4">
                    This guide provides general information only. For detailed or complex cases, refer to:
                  </p>
                  <ul className="space-y-2 text-slate-700">
                    <li className="flex items-start space-x-2">
                      <span className="text-primary-600 mt-1">•</span>
                      <span>Department of Home Affairs — Student Visa Conditions</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-primary-600 mt-1">•</span>
                      <span>Fair Work Ombudsman</span>
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Bottom Line */}
            <section className="bg-primary-600 rounded-lg p-8 text-white">
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-4">✅ Bottom Line</h2>
                <p className="text-lg mb-4">
                  Hiring international students is safe, legal, and beneficial.
                </p>
                <p className="text-lg">
                  With Joborra, you can hire with confidence — we handle the compliance checks so you don't have to.
                </p>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
};

export default EmployerVisaGuidePage;
