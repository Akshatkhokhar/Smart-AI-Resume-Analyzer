import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Search, Zap, CheckCircle, PenTool, TrendingUp, Users, Award, ArrowRight } from 'lucide-react';

const FeatureCard = ({ icon, title, description, delay }) => (
    <div className={`bg-gray-800 p-8 rounded-2xl border border-gray-700 hover:border-blue-500 transition-all duration-300 hover:transform hover:-translate-y-2 group animate-fadeIn`} style={{ animationDelay: `${delay}ms` }}>
        <div className="w-14 h-14 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6 text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-colors">
            {icon}
        </div>
        <h3 className="text-2xl font-bold text-white mb-3">{title}</h3>
        <p className="text-gray-400 leading-relaxed">{description}</p>
    </div>
);

const StatCard = ({ number, label, icon }) => (
    <div className="text-center p-6 bg-gray-800/50 rounded-2xl border border-gray-700 backdrop-blur-sm">
        <div className="flex justify-center mb-4 text-blue-400">
            {icon}
        </div>
        <div className="text-3xl font-bold text-white mb-2">{number}</div>
        <div className="text-gray-400 font-medium">{label}</div>
    </div>
);

const StepCard = ({ number, title, description }) => (
    <div className="relative flex flex-col items-center text-center p-6">
        <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-xl font-bold text-white mb-4 shadow-lg shadow-blue-500/30 z-10">
            {number}
        </div>
        <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
        <p className="text-gray-400">{description}</p>

        {/* Connector Line for larger screens */}
        {number < 3 && (
            <div className="hidden md:block absolute top-12 left-1/2 w-full h-0.5 bg-gray-700 -z-0"></div>
        )}
    </div>
);

const Home = () => {
    return (
        <div className="min-h-screen bg-gray-900 overflow-hidden">
            {/* Hero Section */}
            <div className="relative pt-20 pb-32 lg:pt-32 lg:pb-48">
                {/* Background Blobs */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full overflow-hidden -z-0 pointer-events-none">
                    <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[100px] mix-blend-screen animate-blob"></div>
                    <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[100px] mix-blend-screen animate-blob animation-delay-2000"></div>
                </div>

                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8 animate-fadeIn">
                        <Zap size={16} />
                        <span>Powered by Advanced AI</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 animate-slideUp">
                        <span className="block text-white mb-2">Craft Your Perfect Career with</span>
                        <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                            Intelligent Resume Analysis
                        </span>
                    </h1>

                    <p className="mt-6 text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed animate-slideUp animation-delay-200">
                        Stop guessing what recruiters want. Our AI analyzes your resume against job descriptions,
                        provides actionable feedback, and helps you build a resume that gets you hired.
                    </p>

                    <div className="mt-10 flex flex-col sm:flex-row gap-6 justify-center animate-slideUp animation-delay-400">
                        <Link
                            to="/analyzer"
                            className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white transition-all duration-200 bg-blue-600 rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg shadow-blue-500/30 hover:scale-105"
                        >
                            <FileText className="mr-2" size={24} />
                            Analyze Resume
                        </Link>
                        <Link
                            to="/builder"
                            className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white transition-all duration-200 bg-purple-600 rounded-xl hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 shadow-lg shadow-purple-500/30 hover:scale-105"
                        >
                            <PenTool className="mr-2" size={24} />
                            Build Resume
                        </Link>
                    </div>


                </div>
            </div>

            {/* Features Section */}
            <div className="py-24 bg-gray-800/30 border-y border-gray-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-white sm:text-5xl mb-4">
                            Everything You Need to Succeed
                        </h2>
                        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                            Comprehensive tools designed to optimize every step of your job application process.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<Zap size={32} />}
                            title="AI Analysis"
                            description="Get instant, detailed feedback on your resume's content, formatting, and impact using state-of-the-art AI models."
                            delay={0}
                        />
                        <FeatureCard
                            icon={<PenTool size={32} />}
                            title="Resume Builder"
                            description="Create professional, ATS-friendly resumes in minutes with our intuitive builder. Multiple templates available."
                            delay={100}
                        />
                        <FeatureCard
                            icon={<Search size={32} />}
                            title="Smart Job Match"
                            description="Find jobs that perfectly match your skills and experience from top platforms like LinkedIn and Indeed."
                            delay={200}
                        />
                        <FeatureCard
                            icon={<TrendingUp size={32} />}
                            title="ATS Score"
                            description="Check your compatibility with Applicant Tracking Systems to ensure your resume never gets filtered out."
                            delay={300}
                        />
                        <FeatureCard
                            icon={<Award size={32} />}
                            title="Skill Gap Analysis"
                            description="Identify missing skills required for your target role and get recommendations on how to acquire them."
                            delay={400}
                        />
                        <FeatureCard
                            icon={<Users size={32} />}
                            title="Interview Prep"
                            description="Get potential interview questions based on your resume and target job description."
                            delay={500}
                        />
                    </div>
                </div>
            </div>

            {/* How It Works Section */}
            <div className="py-24 bg-gray-900">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-white sm:text-4xl mb-4">
                            How It Works
                        </h2>
                        <p className="text-gray-400">
                            Three simple steps to your dream job
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
                        <StepCard
                            number={1}
                            title="Upload or Build"
                            description="Upload your existing resume or create a new one from scratch using our builder."
                        />
                        <StepCard
                            number={2}
                            title="Analyze & Optimize"
                            description="Get instant AI feedback and optimize your resume for ATS and recruiters."
                        />
                        <StepCard
                            number={3}
                            title="Apply with Confidence"
                            description="Find matching jobs and apply with a resume that stands out."
                        />
                    </div>
                </div>
            </div>

            {/* CTA Section */}
            <div className="py-20 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-900/40 to-purple-900/40"></div>
                <div className="max-w-4xl mx-auto px-4 relative z-10 text-center">
                    <h2 className="text-4xl font-bold text-white mb-8">
                        Ready to Accelerate Your Career?
                    </h2>
                    <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
                        Join thousands of job seekers who have successfully landed interviews using Smart Resume AI.
                    </p>
                    <Link
                        to="/analyzer"
                        className="inline-flex items-center justify-center px-10 py-5 text-xl font-bold text-white transition-all duration-200 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full hover:from-blue-700 hover:to-purple-700 shadow-xl shadow-blue-500/20 hover:scale-105"
                    >
                        Get Started for Free <ArrowRight className="ml-2" />
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Home;
