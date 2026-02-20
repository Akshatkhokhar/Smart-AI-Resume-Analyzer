import React, { useState } from 'react';
import { Search, MapPin, Briefcase, DollarSign, ExternalLink, Loader } from 'lucide-react';
import api from '../services/api';

const JobSearch = () => {
    const [jobTitle, setJobTitle] = useState('');
    const [location, setLocation] = useState('');
    const [experience, setExperience] = useState('all');
    const [loading, setLoading] = useState(false);
    const [jobs, setJobs] = useState([]);
    const [searched, setSearched] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!jobTitle) return;

        setLoading(true);
        setSearched(true);
        try {
            const response = await api.get('/jobs/search', {
                params: {
                    title: jobTitle,
                    location: location,
                    experience: experience
                }
            });
            setJobs(response.data);
        } catch (error) {
            console.error("Error searching jobs:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent mb-4">
                        Smart Job Search
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Find your dream job across multiple platforms in one click
                    </p>
                </div>

                {/* Search Form */}
                <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-6 mb-12">
                    <form onSubmit={handleSearch} className="space-y-4 md:space-y-0 md:flex md:items-end md:gap-4">
                        <div className="flex-1 space-y-2">
                            <label className="text-sm font-medium text-gray-300">Job Title / Skills</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-3 text-gray-500" size={20} />
                                <input
                                    type="text"
                                    value={jobTitle}
                                    onChange={(e) => setJobTitle(e.target.value)}
                                    placeholder="e.g. Software Engineer"
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                                    required
                                />
                            </div>
                        </div>

                        <div className="flex-1 space-y-2">
                            <label className="text-sm font-medium text-gray-300">Location</label>
                            <div className="relative">
                                <MapPin className="absolute left-3 top-3 text-gray-500" size={20} />
                                <input
                                    type="text"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                    placeholder="e.g. Bangalore"
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                                />
                            </div>
                        </div>

                        <div className="w-full md:w-48 space-y-2">
                            <label className="text-sm font-medium text-gray-300">Experience</label>
                            <select
                                value={experience}
                                onChange={(e) => setExperience(e.target.value)}
                                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none appearance-none"
                            >
                                <option value="all">All Levels</option>
                                <option value="fresher">Fresher</option>
                                <option value="0-1">0-1 Years</option>
                                <option value="1-3">1-3 Years</option>
                                <option value="3-5">3-5 Years</option>
                                <option value="5-7">5-7 Years</option>
                                <option value="7+">7+ Years</option>
                            </select>
                        </div>

                        <div className="w-full md:w-auto">
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 px-8 rounded-lg transition-colors flex items-center justify-center gap-2"
                            >
                                {loading ? <Loader className="animate-spin" size={20} /> : <Search size={20} />}
                                Search
                            </button>
                        </div>
                    </form>
                </div>

                {/* Results */}
                {loading ? (
                    <div className="flex justify-center py-12">
                        <Loader className="animate-spin text-blue-500" size={48} />
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {searched && jobs.length === 0 && (
                            <div className="col-span-full text-center py-12 text-gray-400">
                                No jobs found. Try adjusting your search criteria.
                            </div>
                        )}
                        {jobs.map((job, index) => (
                            <div key={index} className="bg-gray-800 rounded-xl border border-gray-700 p-6 hover:border-blue-500/50 transition-all hover:transform hover:-translate-y-1 group">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div>
                                            <h3 className="font-semibold text-white line-clamp-1">{job.portal}</h3>
                                            <span className="text-xs text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded-full">New</span>
                                        </div>
                                    </div>
                                </div>

                                <h4 className="text-lg font-bold text-gray-200 mb-2 line-clamp-2 min-h-[3.5rem]">
                                    {job.title}
                                </h4>

                                <div className="flex items-center gap-2 text-gray-400 text-sm mb-6">
                                    <MapPin size={16} />
                                    {location || "India"}
                                </div>

                                <a
                                    href={job.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center justify-center gap-2 w-full bg-gray-700 hover:bg-blue-600 text-white py-2 rounded-lg transition-colors group-hover:bg-blue-600"
                                >
                                    Apply Now
                                    <ExternalLink size={16} />
                                </a>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default JobSearch;
