import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Users, Briefcase, TrendingUp, CheckCircle, Star, Shield, GraduationCap, Brain, RefreshCw, ArrowRight } from 'lucide-react';

import Card from '../components/ui/Card';
import DisabledLink from '../components/ui/DisabledLink';
import { useAuth } from '../contexts/AuthContext';

const HomePage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  const challenges = [
    {
      problem: '❌ Traditional job boards show everything',
      solution: '✅ We show only visa-friendly opportunities',
      impact: 'Save 15+ hours per week on irrelevant applications'
    },
    {
      problem: '❌ No way to know if companies sponsor visas',
      solution: '✅ AI-powered visa sponsorship detection',
      impact: '95% accuracy in identifying sponsor-friendly employers'
    },
    {
      problem: '❌ Student work restrictions are confusing',
      solution: '✅ Clear work rights compliance indicators',
      impact: 'Never risk violating your visa conditions'
    },
    {
      problem: '❌ Generic job descriptions hide key details',
      solution: '✅ Visa-specific information highlighted upfront',
      impact: 'Make informed decisions before applying'
    }
  ];

  const features = [
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Visa-Friendly Jobs",
      description: "Curated opportunities from accredited sponsors who can support your visa application.",
      highlights: ["Student Visa (subclass 500)", "Temporary Graduate (subclass 485)", "Employer Sponsored TSS (subclass 482)"],
      color: "text-blue-600 bg-blue-100"
    },
    {
      icon: <GraduationCap className="h-8 w-8" />,
      title: "Student-Friendly Positions",
      description: "Part-time and casual roles that comply with student visa work restrictions.",
      highlights: ["48 hours per fortnight limit", "Holiday work rights", "Course-related experience"],
      color: "text-green-600 bg-green-100"
    },
    {
      icon: <Brain className="h-8 w-8" />,
      title: "AI-Powered Matching",
      description: "Smart algorithms match your skills and visa status with the right opportunities.",
      highlights: ["Skill assessment", "Visa compatibility", "Career progression"],
      color: "text-purple-600 bg-purple-100"
    },
    {
      icon: <RefreshCw className="h-8 w-8" />,
      title: "Real-Time Updates",
      description: "Fresh job listings updated daily from trusted sources and company career pages.",
      highlights: ["Daily updates", "Verified employers", "Direct applications"],
      color: "text-orange-600 bg-orange-100"
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Post a Job in Under 2 Minutes",
      description: "Quick and easy job posting process for employers to find the perfect candidates.",
      highlights: ["Simple form", "AI-generated job descriptions", "Instant publishing"],
      color: "text-red-600 bg-red-100"
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Visa Verification",
      description: "Integrated visa status verification to ensure you're applying for jobs you're eligible for.",
      highlights: ["VEVO integration", "Work rights validation", "Compliance tracking"],
      color: "text-teal-600 bg-teal-100"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section (light background like mock) */}
      <div className="bg-gradient-to-b from-white to-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 md:py-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            {/* Left: Headline + subcopy + search */}
            <div>
              <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
                <span className="block">Get Matched with</span>
                <span className="block">Perfect Opportunities.</span>
                <span className="block text-primary-700">Built for international</span>
                <span className="block text-primary-700">students. Backed by</span>
                <span className="block text-primary-700">real employers.</span>
              </h1>
              <p className="mt-5 text-slate-600 max-w-2xl">
                Complete your profile and we'll match you with visa-friendly opportunities 
                that fit your skills and career goals.
              </p>
              <p className="mt-2 text-slate-600 max-w-2xl">
                No endless searching. No cold applications. Just personalized matches delivered to your inbox.
              </p>
              {/* Badges */}
              <div className="mt-4 flex flex-wrap gap-2 sm:gap-3 text-xs sm:text-sm">
                <span className="inline-flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-full bg-green-50 text-green-700 border border-green-200">
                  ✅ 100% Visa Friendly
                </span>
                <span className="inline-flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  🎯 AI‑Powered Matching
                </span>
                <span className="inline-flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                  📧 Email Matches
                </span>
              </div>
              {/* CTAs for Profile Completion and Matching */}
              <div className="mt-8 flex flex-col sm:flex-row gap-4 max-w-2xl">
                {!isAuthenticated ? (
                  <>
                    <Link to="/auth?tab=login" className="flex-1">
                      <button className="w-full inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl">
                        <Brain className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                        <span className="text-center">Complete Profile & Get Matched</span>
                      </button>
                    </Link>
                    <Link to="/auth?tab=login" className="flex-1">
                      <button className="w-full inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-transparent border-2 border-primary-600 text-primary-600 hover:bg-primary-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 hover:shadow-lg">
                        <Users className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                        <span className="text-center">Find Perfect Candidates</span>
                      </button>
                    </Link>
                  </>
                ) : user?.role === 'student' ? (
                  <>
                    <Link to="/profile" className="flex-1">
                      <button className="w-full inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl">
                        <Brain className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                        <span className="text-center">Complete Profile & Get Matched</span>
                      </button>
                    </Link>
                    <span className="flex-1 inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-transparent border-2 border-gray-300 text-gray-400 cursor-not-allowed">
                      <Users className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                      <span className="text-center">Find Perfect Candidates</span>
                    </span>
                  </>
                ) : user?.role === 'employer' ? (
                  <>
                    <span className="flex-1 inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-transparent border-2 border-gray-300 text-gray-400 cursor-not-allowed">
                      <Brain className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                      <span className="text-center">Complete Profile & Get Matched</span>
                    </span>
                    <Link to="/employer/post-job" className="flex-1">
                      <button className="w-full inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-transparent border-2 border-primary-600 text-primary-600 hover:bg-primary-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 hover:shadow-lg">
                        <Users className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                        <span className="text-center">Find Perfect Candidates</span>
                      </button>
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to="/auth?tab=login" className="flex-1">
                      <button className="w-full inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl">
                        <Brain className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                        <span className="text-center">Complete Profile & Get Matched</span>
                      </button>
                    </Link>
                    <Link to="/auth?tab=login" className="flex-1">
                      <button className="w-full inline-flex items-center justify-center px-4 sm:px-6 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl bg-transparent border-2 border-primary-600 text-primary-600 hover:bg-primary-600 hover:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 hover:shadow-lg">
                        <Users className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
                        <span className="text-center">Find Perfect Candidates</span>
                      </button>
                    </Link>
                  </>
                )}
              </div>
              <p className="mt-4 text-sm text-slate-600 max-w-2xl">
                We'll match you with the best opportunities and candidates behind the scenes. 
                Complete your profile and we'll email you personalized matches.
              </p>
            </div>
            {/* Right: Hero image */}
            <div className="hidden lg:block">
              <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-sm">
                <img
                  src="/hero-home.jpg"
                  alt="Students finding visa-friendly jobs in Australia"
                  className="w-full h-[420px] lg:h-[440px] object-cover object-[center_20%]"
                  loading="eager"
                />
              </div>
            </div>
          </div>
        </div>
      </div>


      {/* Features Section */}
      <div className="bg-slate-50 py-12 sm:py-16 lg:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16 lg:mb-20">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-4 sm:mb-6">Why You Should Choose Joborra</h2>
            <p className="text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
              We're not just another job board. We're your dedicated partner in navigating Australia's job market 
              with tools built specifically for international students and visa holders.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 lg:gap-10">
            {features.map((feature, index) => (
              <Card key={index} className="p-6 sm:p-8 bg-white">
                <div className={`inline-flex items-center justify-center w-12 h-12 sm:w-16 sm:h-16 rounded-xl text-cyan-700 bg-cyan-100 mb-4 sm:mb-6`}>
                  {feature.icon}
                </div>
                <h3 className="text-lg sm:text-xl font-semibold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-sm sm:text-base text-slate-600 mb-4 sm:mb-6 leading-relaxed">{feature.description}</p>
                <ul className="space-y-2 sm:space-y-3">
                  {feature.highlights.map((highlight, idx) => (
                    <li key={idx} className="flex items-center text-slate-700 text-sm sm:text-base">
                      <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 text-cyan-600 mr-2 sm:mr-3 flex-shrink-0" />
                      {highlight}
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* About Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-4">
                Built for International Professionals
              </h2>
              <p className="text-slate-600 mb-4">
                Joborra was created by international professionals who understand 
                the complexities of finding employment in Australia. We've experienced 
                the visa requirements, the job market challenges, and the need for 
                reliable information.
              </p>
              <div className="space-y-4">
                <div className="flex items-start">
                  <Star className="h-6 w-6 text-cyan-600 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-slate-900">Verified Opportunities</h4>
                    <p className="text-slate-600">Every job is verified for visa sponsorship potential and work rights compliance.</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <Users className="h-6 w-6 text-cyan-600 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-slate-900">Community Support</h4>
                    <p className="text-slate-600">Connect with other international professionals and share experiences.</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <TrendingUp className="h-6 w-6 text-cyan-600 mr-3 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-slate-900">Career Growth</h4>
                    <p className="text-slate-600">Find opportunities that align with your career goals and visa pathway.</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="bg-slate-50 rounded-2xl p-8 border border-slate-200">
                <div className="grid grid-cols-2 gap-6">
                  <div className="bg-white rounded-xl p-6 text-center border border-slate-200">
                    <Briefcase className="h-8 w-8 text-cyan-600 mx-auto mb-3" />
                    <div className="text-2xl font-bold text-slate-900">High</div>
                    <div className="text-sm text-slate-600">Success Rate</div>
                  </div>
                  <div className="bg-white rounded-xl p-6 text-center border border-slate-200">
                    <Search className="h-8 w-8 text-cyan-600 mx-auto mb-3" />
                    <div className="text-2xl font-bold text-slate-900">Daily</div>
                    <div className="text-sm text-slate-600">Job Updates</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem vs Solution */}
      <div className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              The Job Search Problems We Solve
            </h2>
            <p className="text-lg text-slate-600">
              Stop wasting time on applications that lead nowhere
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {challenges.map((challenge, index) => (
              <Card key={index} className="p-6 bg-white">
                <div className="space-y-4">
                  <div className="text-red-600 font-medium">{challenge.problem}</div>
                  <div className="text-green-600 font-medium">{challenge.solution}</div>
                  <div className="text-slate-600 text-sm bg-slate-50 p-3 rounded-lg">
                    <strong>Impact:</strong> {challenge.impact}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <section className="py-16 bg-cyan-700 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Ready to Start Your Australian Career Journey?
          </h2>
          <p className="text-lg mb-8 opacity-90">
            Join thousands of international professionals who have found their dream jobs in Australia.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {!isAuthenticated && (
              <Link to="/auth?tab=register">
                <button className="inline-flex items-center justify-center px-6 py-3 text-lg font-semibold rounded-xl bg-white text-cyan-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-cyan-700 transition-colors duration-200 shadow-lg">
                  <ArrowRight className="w-5 h-5 mr-2" />
                  Create Your Profile
                </button>
              </Link>
            )}
            {isAuthenticated && user?.role === 'employer' ? (
              <Link to="/employer/post-job">
                <button className="inline-flex items-center justify-center px-6 py-3 text-lg font-semibold rounded-xl bg-transparent border-2 border-white text-white hover:bg-white hover:text-cyan-700 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-cyan-700 transition-colors duration-200">
                  Post Opportunities
                </button>
              </Link>
            ) : (
              <span className="inline-flex items-center justify-center px-6 py-3 text-lg font-semibold rounded-xl bg-transparent border-2 border-white text-white opacity-50 cursor-not-allowed relative">
                <DisabledLink className="text-white">Explore Opportunities</DisabledLink>
              </span>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
