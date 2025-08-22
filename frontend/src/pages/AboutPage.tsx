import React from 'react';
import { Shield, Briefcase, GraduationCap, Globe2 } from 'lucide-react';
import Card from '../components/ui/Card';

const AboutPage: React.FC = () => {
  const pillars = [
    {
      icon: <Shield className="h-6 w-6 text-green-600" />,
      title: 'Visa Compliance',
      desc: 'Every listing is checked for visa sponsorship potential and student work-rights compliance.'
    },
    {
      icon: <GraduationCap className="h-6 w-6 text-blue-600" />,
      title: 'Student First',
      desc: 'Built for international students and graduates navigating the Australian job market.'
    },
    {
      icon: <Briefcase className="h-6 w-6 text-purple-600" />,
      title: 'Quality Jobs',
      desc: 'We aggregate from official ATS APIs and trusted sources to ensure reliability.'
    },
    {
      icon: <Globe2 className="h-6 w-6 text-orange-600" />,
      title: 'Australia-wide',
      desc: 'Opportunities across major cities and regional areas, updated continuously.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-3">About Joborra</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Joborra helps international students and professionals find visa-friendly, student-friendly roles in Australia.
            We combine verified sources with smart filtering and clean UX to accelerate your job search.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {pillars.map((p, i) => (
            <Card key={i} className="p-6">
              <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center mb-3">
                {p.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">{p.title}</h3>
              <p className="text-sm text-gray-600">{p.desc}</p>
            </Card>
          ))}
        </div>

        <Card className="p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Our Approach</h2>
          <p className="text-gray-700 leading-relaxed">
            We focus on clarity and trust. Listings are sourced via official ATS APIs and legitimate aggregators, then analysed with
            visa-friendly and student-friendly indicators. Our UI is designed to reduce noise, surface critical information, and help you
            apply faster with confidence.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default AboutPage;
