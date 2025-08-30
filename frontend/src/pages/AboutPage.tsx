import React, { useState, useEffect } from 'react';
import { Shield, Briefcase, GraduationCap, Globe2, Users, TrendingUp, CheckCircle, Star, Clock, Target, Heart, Zap } from 'lucide-react';
import Card from '../components/ui/Card';
import { JobStats } from '../types';
import apiService from '../services/api';

const AboutPage: React.FC = () => {
  const [stats, setStats] = useState<JobStats | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiService.getJobStats();
        setStats(response);
      } catch (error) {
        console.error('Failed to fetch job stats:', error);
      }
    };
    fetchStats();
  }, []);

  const valueProps = [
    {
      icon: <Shield className="h-8 w-8 text-green-600" />,
      title: 'Visa-Safe Job Search',
      description: 'Every job is analyzed for visa sponsorship potential. No more applying to roles that can\'t sponsor you.',
      benefits: ['482 TSS Visa Support', '186 ENS Visa Opportunities', 'Student Work Rights Compliance'],
      color: 'bg-green-50 border-green-200'
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-600" />,
      title: 'Save 10+ Hours Per Week',
      description: 'Stop wasting time on irrelevant applications. Our AI filters show only jobs that match your visa status.',
      benefits: ['Smart Job Matching', 'Instant Visa Compatibility', 'One-Click Applications'],
      color: 'bg-yellow-50 border-yellow-200'
    },
    {
      icon: <Users className="h-8 w-8 text-blue-600" />,
      title: 'Built by International Students',
      description: 'We\'ve been in your shoes. Our platform solves the exact problems we faced during our own job searches.',
      benefits: ['Real Student Experiences', 'Community Support', 'Peer-to-Peer Advice'],
      color: 'bg-blue-50 border-blue-200'
    },
    {
      icon: <Target className="h-8 w-8 text-purple-600" />,
      title: 'Direct Employer Connections',
      description: 'Connect directly with companies that actively hire international talent and understand visa processes.',
      benefits: ['Verified Employers', 'Direct Applications', 'No Recruitment Agencies'],
      color: 'bg-purple-50 border-purple-200'
    }
  ];

  const successStories = [
    {
      name: 'Priya S.',
      role: 'Software Engineer',
      university: 'University of Melbourne',
      visa: 'TSS 482',
      story: 'Found my dream job at a tech startup in 3 weeks. The visa sponsorship filter saved me from applying to 20+ companies that couldn\'t sponsor.',
      company: 'TechCorp Australia',
      location: 'Melbourne',
      avatar: '👩‍💻'
    },
    {
      name: 'Ahmed K.',
      role: 'Data Analyst',
      university: 'UNSW Sydney',
      visa: 'Student 500',
      story: 'As a student, I needed part-time work that complied with my visa. Joborra showed me exactly which companies hire students.',
      company: 'Finance Solutions',
      location: 'Sydney',
      avatar: '👨‍💼'
    },
    {
      name: 'Maria L.',
      role: 'Marketing Coordinator',
      university: 'Queensland University',
      visa: 'Graduate 485',
      story: 'The transition from student to work visa was seamless with Joborra. Found a company that sponsored my 482 visa.',
      company: 'Digital Marketing Co.',
      location: 'Brisbane',
      avatar: '👩‍🎨'
    }
  ];

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

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-white to-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
              We're International Students Too
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto mb-8">
              We built Joborra because we struggled with the same visa and job search challenges you face. 
              Now we're helping thousands of international students find their dream jobs in Australia.
            </p>
            
            {/* Live Stats */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
                <div className="bg-white rounded-xl p-6 shadow-sm border">
                  <div className="text-3xl font-bold text-primary-600 mb-1">
                    {stats.total_jobs?.toLocaleString() || '0'}
                  </div>
                  <div className="text-sm text-slate-600">Active Jobs</div>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm border">
                  <div className="text-3xl font-bold text-green-600 mb-1">
                    {stats.visa_friendly_jobs?.toLocaleString() || '0'}
                  </div>
                  <div className="text-sm text-slate-600">Visa-Friendly</div>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm border">
                  <div className="text-3xl font-bold text-blue-600 mb-1">
                    {stats.student_friendly_jobs?.toLocaleString() || '0'}
                  </div>
                  <div className="text-sm text-slate-600">Student-Friendly</div>
                </div>
                <div className="bg-white rounded-xl p-6 shadow-sm border">
                  <div className="text-3xl font-bold text-purple-600 mb-1">
                    500+
                  </div>
                  <div className="text-sm text-slate-600">Verified Companies</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Value Propositions */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Why 10,000+ Students Choose Joborra
            </h2>
            <p className="text-lg text-slate-600 max-w-3xl mx-auto">
              We solve the real problems international students face when job hunting in Australia
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {valueProps.map((prop, index) => (
              <Card key={index} className={`p-8 ${prop.color} border-2`}>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {prop.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-900 mb-3">{prop.title}</h3>
                    <p className="text-slate-700 mb-4">{prop.description}</p>
                    <ul className="space-y-2">
                      {prop.benefits.map((benefit, idx) => (
                        <li key={idx} className="flex items-center text-slate-700">
                          <CheckCircle className="h-4 w-4 text-green-600 mr-2 flex-shrink-0" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

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

      {/* Success Stories */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Real Success Stories
            </h2>
            <p className="text-lg text-slate-600">
              See how international students are landing their dream jobs
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {successStories.map((story, index) => (
              <Card key={index} className="p-6 bg-slate-50">
                <div className="text-center mb-4">
                  <div className="text-4xl mb-2">{story.avatar}</div>
                  <h4 className="font-bold text-slate-900">{story.name}</h4>
                  <p className="text-sm text-slate-600">{story.role} at {story.company}</p>
                  <p className="text-xs text-slate-500">{story.university} • {story.visa}</p>
                </div>
                <blockquote className="text-slate-700 italic mb-4">
                  "{story.story}"
                </blockquote>
                <div className="flex items-center justify-between text-sm text-slate-600">
                  <span>📍 {story.location}</span>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-500 mr-1" />
                    <span>Success</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Our Mission */}
      <div className="py-20 bg-primary-700 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Heart className="h-16 w-16 mx-auto mb-6 text-primary-200" />
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Our Mission
          </h2>
          <p className="text-xl mb-8 opacity-90">
            To eliminate the visa-related barriers that prevent international students from finding meaningful employment in Australia. 
            We believe every international student deserves equal access to career opportunities.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold mb-2">95%</div>
              <div className="text-primary-200">Success Rate</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">24/7</div>
              <div className="text-primary-200">Job Updates</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">100%</div>
              <div className="text-primary-200">Visa-Safe</div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="py-16 bg-slate-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">
            Ready to Find Your Dream Job?
          </h2>
          <p className="text-lg text-slate-600 mb-8">
            Join thousands of international students who have already found their perfect match
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/auth"
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 transition-colors"
            >
              Start Your Job Search
            </a>
            <a
              href="/jobs"
              className="inline-flex items-center justify-center px-6 py-3 border border-slate-300 text-base font-medium rounded-md text-slate-700 bg-white hover:bg-slate-50 transition-colors"
            >
              Browse Jobs
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
