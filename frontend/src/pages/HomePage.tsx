import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Users, Briefcase, TrendingUp, CheckCircle, Star, Shield, GraduationCap, Brain, RefreshCw, MapPin, ArrowRight } from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import SearchBar from '../components/home/SearchBar';
import { JobStats } from '../types';
import apiService from '../services/api';

const HomePage: React.FC = () => {
  const [stats, setStats] = useState<JobStats | null>(null);
  // removed unused loading state

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiService.getJobStats();
        setStats(response);
      } catch (error) {
        console.error('Failed to fetch job stats:', error);
      } finally {
        // no-op
      }
    };

    fetchStats();
  }, []);

  const features = [
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Visa-Friendly Jobs",
      description: "Curated opportunities from accredited sponsors who can support your visa application.",
      highlights: ["482 TSS Visa", "186 ENS Visa", "494 Regional Visa"],
      color: "text-blue-600 bg-blue-100"
    },
    {
      icon: <GraduationCap className="h-8 w-8" />,
      title: "Student-Friendly Positions",
      description: "Part-time and casual roles that comply with student visa work restrictions.",
      highlights: ["20 hours/week limit", "Holiday work rights", "Course-related experience"],
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
      icon: <MapPin className="h-8 w-8" />,
      title: "Australia-wide Coverage",
      description: "Jobs across all major Australian cities and regional areas with detailed location insights.",
      highlights: ["Sydney, Melbourne, Brisbane", "Perth, Adelaide, Canberra", "Regional opportunities"],
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
              <h1 className="text-[34px] md:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
                <span className="block">Find Your Next</span>
                <span className="block">Opportunity.</span>
                <span className="block text-primary-700">Built for international</span>
                <span className="block text-primary-700">students. Backed by</span>
                <span className="block text-primary-700">real employers.</span>
              </h1>
              <p className="mt-5 text-slate-600 max-w-2xl">
                Every job here is confirmed to be international student friendly and visa‑verified.
                No cold calls. No guesswork. Just real opportunities, made for you.
              </p>
              {/* Badges */}
              <div className="mt-4 flex flex-wrap gap-3 text-sm">
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-50 text-green-700 border border-green-200">
                  ✅ 100% Verified
                </span>
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  Visa‑Friendly
                </span>
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                  Student‑Approved
                </span>
              </div>
              {/* Search */}
              <div className="mt-6 max-w-2xl">
                <SearchBar onSearch={() => { /* route to /jobs later */ }} />
              </div>
              {/* Popular chips */}
              <div className="mt-4 flex flex-wrap gap-2">
                {['Developer Jobs','Visa Sponsorship','Remote Internships','Part‑Time Roles','Melbourne','Work Type','Remote Friendly','Salary'].map((chip) => (
                  <button key={chip} className="px-3 py-1.5 rounded-full text-sm bg-slate-100 text-slate-700 hover:bg-slate-200">{chip}</button>
                ))}
              </div>
            </div>
            {/* Right: Hero image */}
            <div className="hidden lg:block">
              <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-sm">
                <img
                  src="/hero-home.jpg"
                  alt="Students finding visa-friendly jobs in Australia"
                  className="w-full h-[420px] object-cover"
                  loading="eager"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      {stats && (
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {stats.total_jobs?.toLocaleString() || '0'}
                </div>
                <div className="text-gray-600">Active Jobs</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {stats.visa_friendly_jobs?.toLocaleString() || '0'}
                </div>
                <div className="text-gray-600">Visa-Friendly</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {stats.student_friendly_jobs?.toLocaleString() || '0'}
                </div>
                <div className="text-gray-600">Student-Friendly</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  500+
                </div>
                <div className="text-gray-600">Companies</div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      <div className="bg-slate-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-6">Why 10,000+ Students Choose Joborra</h2>
            <p className="text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
              We're not just another job board. We're your dedicated partner in navigating Australia's job market 
              with tools built specifically for international students and visa holders.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
            {features.map((feature, index) => (
              <Card key={index} className="p-8 bg-white">
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-xl text-cyan-700 bg-cyan-100 mb-6`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 mb-6 leading-relaxed">{feature.description}</p>
                <ul className="space-y-3">
                  {feature.highlights.map((highlight, idx) => (
                    <li key={idx} className="flex items-center text-slate-700">
                      <CheckCircle className="h-5 w-5 text-cyan-600 mr-3 flex-shrink-0" />
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
                    <div className="text-2xl font-bold text-slate-900">95%</div>
                    <div className="text-sm text-slate-600">Success Rate</div>
                  </div>
                  <div className="bg-white rounded-xl p-6 text-center border border-slate-200">
                    <Search className="h-8 w-8 text-cyan-600 mx-auto mb-3" />
                    <div className="text-2xl font-bold text-slate-900">24/7</div>
                    <div className="text-sm text-slate-600">Job Updates</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

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
            <Link to="/auth">
              <Button size="lg" className="bg-white text-cyan-700 hover:bg-slate-100" icon={<ArrowRight className="w-5 h-5" />}>
                Create Your Profile
              </Button>
            </Link>
            <Link to="/jobs">
              <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-cyan-700">
                Explore Opportunities
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
