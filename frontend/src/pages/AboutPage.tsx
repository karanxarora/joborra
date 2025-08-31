import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Lightbulb, CheckCircle, GraduationCap, Globe, Rocket, Star, Users, Shield, Target } from 'lucide-react';
import Card from '../components/ui/Card';
import { useAuth } from '../contexts/AuthContext';

const AboutPage: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-white to-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
              Our Story
            </h1>
            <div className="max-w-4xl mx-auto text-lg text-slate-600 leading-relaxed space-y-6">
              <p>
                Joborra was born from lived experience.
              </p>
              <p>
                Our founder, <strong>Manav Arora</strong>, came to Australia as an international student to study a Bachelor of IT and Bachelor of Business at the University of Newcastle. Like many international students, he quickly realised that finding a job wasn't as simple as sending out applications.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-8">
                <Card className="p-6 bg-cyan-50 border-cyan-200">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Users className="w-6 h-6 text-primary-600" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-3">Access Barriers</h3>
                    <p className="text-slate-700">Too many jobs weren't actually open to international students.</p>
                  </div>
                </Card>
                <Card className="p-6 bg-cyan-50 border-cyan-200">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Shield className="w-6 h-6 text-primary-600" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-3">Compliance Confusion</h3>
                    <p className="text-slate-700">Visa rules and compliance created constant uncertainty.</p>
                  </div>
                </Card>
                <Card className="p-6 bg-cyan-50 border-cyan-200">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Target className="w-6 h-6 text-primary-600" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-3">Employer Uncertainty</h3>
                    <p className="text-slate-700">Employers often weren't sure what students could or couldn't do.</p>
                  </div>
                </Card>
              </div>
              <p>
                The result? Countless rejections, wasted applications, and missed opportunities.
              </p>
              <p className="text-primary-700 font-semibold">
                Manav knew there had to be a better way. That's why he created Joborra — a platform built by an international student, for international students — to make job searching easier, fairer, and more transparent.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Our Mission */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-primary-50 to-cyan-50 rounded-2xl p-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mr-4">
                  <Lightbulb className="w-6 h-6 text-primary-600" />
                </div>
                <h2 className="text-2xl md:text-3xl font-bold text-slate-900">
                  Our Mission
                </h2>
              </div>
              <p className="text-lg text-slate-700 max-w-3xl mx-auto">
                To empower international students with equal access to real job opportunities, while helping employers hire confidently and inclusively.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* What We Do */}
      <div className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-8 text-center">
            What We Do
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="p-6 bg-cyan-50 border-cyan-200">
              <div className="text-center">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <GraduationCap className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">For Students</h3>
                <p className="text-slate-700">
                  Every job listing on Joborra is verified as visa-compliant and student-eligible, so you never waste time applying to roles you can't legally do.
                </p>
              </div>
            </Card>
            <Card className="p-6 bg-cyan-50 border-cyan-200">
              <div className="text-center">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Users className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">For Employers</h3>
                <p className="text-slate-700">
                  We simplify hiring international students by handling the compliance checks and connecting you with motivated, resilient, globally minded talent.
                </p>
              </div>
            </Card>
            <Card className="p-6 bg-cyan-50 border-cyan-200">
              <div className="text-center">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">For Partners</h3>
                <p className="text-slate-700">
                  We collaborate with universities, programs, and networks like Bridge2Work and the I2N Accelerator to create scalable impact.
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Why Joborra */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-8 text-center">
            Why Joborra?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <GraduationCap className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="font-bold text-slate-900 mb-2">Built on Real Experience</h3>
              <p className="text-sm text-slate-600">Founded by a student who lived the challenges firsthand.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="font-bold text-slate-900 mb-2">Verified Jobs Only</h3>
              <p className="text-sm text-slate-600">Every role is checked for compliance before it's posted.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Globe className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="font-bold text-slate-900 mb-2">Inclusive Hiring Made Easy</h3>
              <p className="text-sm text-slate-600">Employers gain access to diverse, driven candidates.</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Rocket className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="font-bold text-slate-900 mb-2">Student-First Platform</h3>
              <p className="text-sm text-slate-600">Designed to remove barriers and unlock potential.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Our Vision */}
      <div className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-2xl p-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-6">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center mr-4">
                  <Star className="w-6 h-6 text-primary-600" />
                </div>
                <h2 className="text-2xl md:text-3xl font-bold text-slate-900">
                  Our Vision
                </h2>
              </div>
              <p className="text-lg text-slate-700 max-w-3xl mx-auto">
                A future where every international student in Australia has equal opportunity to succeed, and every employer benefits from their unique skills and perspectives.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Backed By */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-8">
              Backed By
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl mx-auto">
              <div className="bg-white border border-slate-200 rounded-lg p-6">
                <h3 className="font-bold text-slate-900 mb-2">University of Newcastle's I2N Accelerator</h3>
                <p className="text-sm text-slate-600">Supporting innovation and entrepreneurship</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-lg p-6">
                <h3 className="font-bold text-slate-900 mb-2">Bridge2Work</h3>
                <p className="text-sm text-slate-600">Connecting students with opportunities</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="py-16 bg-cyan-700 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Join us on our mission.
          </h2>
          <p className="text-lg mb-8 opacity-90">
            Whether you're a student searching for opportunity, an employer seeking talent, or a partner ready to create impact — Joborra is here to make hiring better, together.
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
            <Link to={isAuthenticated && user?.role === 'employer' ? "/employer/post-job" : "/jobs"}>
              <button className="inline-flex items-center justify-center px-6 py-3 text-lg font-semibold rounded-xl bg-transparent border-2 border-white text-white hover:bg-white hover:text-cyan-700 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-cyan-700 transition-colors duration-200">
                {isAuthenticated && user?.role === 'employer' ? 'Post Opportunities' : 'Explore Opportunities'}
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;