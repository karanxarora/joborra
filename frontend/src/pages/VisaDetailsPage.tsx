import React from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { ArrowLeft, Clock, Briefcase, MapPin, GraduationCap, Users } from 'lucide-react';

const VisaDetailsPage: React.FC = () => {
  const visaTypes = [
    {
      name: 'Student Visa (subclass 500)',
      description: 'International student visa for studying in Australia',
      workRestrictions: 'Up to 48 hours per fortnight during study periods, unlimited during scheduled breaks',
      exampleJobs: 'Retail, hospitality, tutoring, casual work, internships related to field of study',
      icon: <GraduationCap className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    },
    {
      name: 'Temporary Graduate (subclass 485)',
      description: 'Post-study work visa for recent graduates',
      workRestrictions: 'Unlimited work rights for up to 2-4 years depending on qualification level',
      exampleJobs: 'Professional roles in field of study, graduate programs, skilled positions',
      icon: <Briefcase className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    },
    {
      name: 'Skilled Independent (subclass 189)',
      description: 'Permanent visa for skilled workers without sponsorship',
      workRestrictions: 'Unlimited work rights, can work in any field',
      exampleJobs: 'Any professional role, management positions, business ownership',
      icon: <Users className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    },
    {
      name: 'Skilled Nominated (subclass 190)',
      description: 'Permanent visa for skilled workers nominated by a state',
      workRestrictions: 'Unlimited work rights, must live in nominating state for 2 years',
      exampleJobs: 'Skilled positions in nominated state, professional roles',
      icon: <MapPin className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    },
    {
      name: 'Skilled Work Regional (subclass 491)',
      description: 'Regional skilled work visa',
      workRestrictions: 'Unlimited work rights, must live and work in regional area',
      exampleJobs: 'Regional professional roles, healthcare, education, agriculture',
      icon: <MapPin className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    },
    {
      name: 'Employer Sponsored TSS (subclass 482)',
      description: 'Temporary Skill Shortage visa (employer-sponsored)',
      workRestrictions: 'Can only work for sponsoring employer in nominated occupation',
      exampleJobs: 'Skilled positions with sponsoring employer, specific occupation roles',
      icon: <Briefcase className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    },
    {
      name: 'Employer Nomination (subclass 186)',
      description: 'Employer Nomination Scheme (permanent)',
      workRestrictions: 'Unlimited work rights, can work in any field after 3 years',
      exampleJobs: 'Permanent professional roles, management positions',
      icon: <Users className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    },
    {
      name: 'Working Holiday (subclass 417/462)',
      description: 'Working holiday visa for young people',
      workRestrictions: 'Can work for same employer for maximum 6 months, study up to 4 months',
      exampleJobs: 'Hospitality, tourism, seasonal work, casual jobs, farm work',
      icon: <Clock className="h-6 w-6" />,
      color: 'bg-cyan-100 text-primary-600'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link to="/employer/post-job" className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Post a Job
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Visa Details & Work Restrictions</h1>
        <p className="mt-2 text-gray-600">
          Understanding different visa types and their work restrictions helps you create better job postings for international students.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {visaTypes.map((visa, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-start space-x-4">
              <div className={`p-3 rounded-lg ${visa.color}`}>
                {visa.icon}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{visa.name}</h3>
                <p className="text-gray-600 mb-4">{visa.description}</p>
                
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Work Restrictions:</h4>
                    <p className="text-sm text-gray-600">{visa.workRestrictions}</p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Example Jobs:</h4>
                    <p className="text-sm text-gray-600">{visa.exampleJobs}</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="mt-8">
        <Card className="p-6 bg-primary-50 border-primary-200">
          <h3 className="text-lg font-semibold text-primary-900 mb-2">Important Notes</h3>
          <ul className="text-sm text-primary-800 space-y-2">
            <li>• Work restrictions may change based on individual visa conditions</li>
            <li>• Students should always check their specific visa conditions before accepting employment</li>
            <li>• Some visas require work to be related to the field of study</li>
            <li>• Regional visas have specific location requirements</li>
            <li>• Employer-sponsored visas are tied to specific employers and occupations</li>
          </ul>
        </Card>
      </div>

      <div className="mt-6 flex justify-center">
        <Link to="/employer/post-job">
          <Button className="bg-primary-600 hover:bg-primary-700">
            Continue Posting Job
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default VisaDetailsPage;
