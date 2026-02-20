import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader, Award, TrendingUp, XCircle, Briefcase, User, GraduationCap, Calendar } from 'lucide-react';
import api from '../services/api';
import CircularProgress from '../components/CircularProgress';

const Analyzer = () => {
    const [file, setFile] = useState(null);
    const [jobDescription, setJobDescription] = useState('');
    const [jobRole, setJobRole] = useState('Software Engineer');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    // Removed downloading state as button is removed

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError("Please upload a resume file.");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('job_description', jobDescription);
        formData.append('job_role', jobRole);

        try {
            const response = await api.post('/resume/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err) {
            console.error(err);
            setError("Analysis failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // Helper to extract structured data
    const getStructuredData = () => {
        if (!result?.ai_analysis) return null;

        let data = result.ai_analysis;

        // Handle if it's nested in structured_data (new backend format)
        if (data.structured_data) {
            return data.structured_data;
        }

        // Handle string parsing if needed (fallback)
        if (typeof data === 'string') {
            try {
                const clean = data.replace(/```json\s*/g, '').replace(/```\s*$/g, '');
                return JSON.parse(clean);
            } catch (e) {
                console.error("Failed to parse string data", e);
                return null;
            }
        }

        return data; // Assume it's already an object
    };

    const structuredData = getStructuredData();

    const jobCategories = {
        "Software Engineering": [
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "Mobile Developer",
            "DevOps Engineer",
            "Software Architect",
            "QA Engineer"
        ],
        "Data Science & Analytics": [
            "Data Scientist",
            "Data Analyst",
            "Machine Learning Engineer",
            "Business Intelligence Analyst",
            "Data Engineer"
        ],
        "Product & Design": [
            "Product Manager",
            "UI/UX Designer",
            "Graphic Designer",
            "Product Designer"
        ],
        "Marketing": [
            "Digital Marketer",
            "Content Strategist",
            "SEO Specialist",
            "Social Media Manager"
        ],
        "Sales & Business": [
            "Sales Representative",
            "Business Development Manager",
            "Account Executive"
        ],
        "Other": [
            "Other"
        ]
    };

    const [selectedCategory, setSelectedCategory] = useState("Software Engineering");
    const [selectedSubRole, setSelectedSubRole] = useState("Frontend Developer");

    // Update jobRole when category or subrole changes
    React.useEffect(() => {
        setJobRole(selectedSubRole);
    }, [selectedSubRole]);

    const handleCategoryChange = (e) => {
        const category = e.target.value;
        setSelectedCategory(category);
        // Reset subrole to first item in new category
        const firstSubRole = jobCategories[category][0];
        setSelectedSubRole(firstSubRole);
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-6xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-4">
                        AI Resume Analyzer
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Upload your resume and get instant feedback powered by Gemini AI
                    </p>
                </div>

                <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-8 mb-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* File Upload */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-300">Upload Resume (PDF)</label>
                            <div className="relative border-2 border-dashed border-gray-600 rounded-lg p-8 hover:border-blue-500 transition-colors text-center cursor-pointer">
                                <input
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleFileChange}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                                <p className="text-gray-300 font-medium">
                                    {file ? file.name : "Click to upload or drag and drop"}
                                </p>
                                <p className="text-gray-500 text-sm mt-1">PDF up to 10MB</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Job Category</label>
                                    <select
                                        value={selectedCategory}
                                        onChange={handleCategoryChange}
                                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none appearance-none cursor-pointer"
                                    >
                                        {Object.keys(jobCategories).map((category) => (
                                            <option key={category} value={category}>{category}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Target Role</label>
                                    {selectedSubRole === 'Other' ? (
                                        <input
                                            type="text"
                                            value={jobRole}
                                            onChange={(e) => setJobRole(e.target.value)}
                                            placeholder="Enter your target role"
                                            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                                        />
                                    ) : (
                                        <select
                                            value={selectedSubRole}
                                            onChange={(e) => setSelectedSubRole(e.target.value)}
                                            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none appearance-none cursor-pointer"
                                        >
                                            {jobCategories[selectedCategory].map((role) => (
                                                <option key={role} value={role}>{role}</option>
                                            ))}
                                        </select>
                                    )}
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Job Description (Optional)</label>
                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    placeholder="Paste job description here for better matching..."
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white h-[42px] focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none overflow-hidden focus:h-32 transition-all duration-300"
                                />
                            </div>
                        </div>

                        <div className="flex justify-center pt-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-3 px-8 rounded-full transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                            >
                                {loading ? <Loader className="animate-spin" /> : <FileText />}
                                {loading ? "Analyzing..." : "Analyze Resume"}
                            </button>
                        </div>
                    </form>
                    {error && (
                        <div className="mt-6 p-4 bg-red-900/50 border border-red-500 rounded-lg flex items-center gap-3 text-red-200">
                            <AlertCircle size={20} />
                            {error}
                        </div>
                    )}
                </div>

                {/* New Structured Results Section */}
                {result && structuredData && (
                    <div className="space-y-8 animate-fade-in">
                        {/* 1. Hero Section: Match Score & Candidate Summary */}
                        <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700 flex flex-col md:flex-row items-center gap-10">
                            {/* Circular Score */}
                            <div className="flex-shrink-0">
                                <CircularProgress score={structuredData.match_score || structuredData.score || 0} size={200} />
                            </div>

                            {/* Summary & Candidate Info */}
                            <div className="flex-1 space-y-6 text-center md:text-left">
                                <div>
                                    <h2 className="text-3xl font-bold text-white mb-2">Overall Match Score</h2>
                                    <p className="text-gray-300 text-lg leading-relaxed">
                                        {structuredData.overall_assessment || structuredData.summary || "Analysis complete."}
                                    </p>
                                </div>

                                {/* Candidate Info Grid */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-gray-900/30 p-4 rounded-xl border border-gray-700/50">
                                    <div className="flex items-center gap-3">
                                        <User className="text-blue-400" size={20} />
                                        <div>
                                            <div className="text-xs text-gray-500">Candidate</div>
                                            <div className="font-semibold text-white">{structuredData.candidate_info?.name || "N/A"}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <Briefcase className="text-purple-400" size={20} />
                                        <div>
                                            <div className="text-xs text-gray-500">Target Role</div>
                                            <div className="font-semibold text-white">{jobRole}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <Calendar className="text-green-400" size={20} />
                                        <div>
                                            <div className="text-xs text-gray-500">Experience</div>
                                            <div className="font-semibold text-white">{structuredData.candidate_info?.experience || "N/A"}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <GraduationCap className="text-yellow-400" size={20} />
                                        <div>
                                            <div className="text-xs text-gray-500">Education</div>
                                            <div className="font-semibold text-white truncate max-w-[200px]" title={structuredData.candidate_info?.education || "N/A"}>
                                                {structuredData.candidate_info?.education || "N/A"}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* 2. Skill Gap Analysis */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Matched Skills */}
                            <div className="bg-gray-800 rounded-2xl p-6 border border-green-500/30 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
                                <h3 className="text-xl font-bold text-green-400 mb-6 flex items-center gap-2">
                                    <CheckCircle size={24} /> Matched Skills
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {(structuredData.matched_skills || structuredData.strengths || []).map((skill, idx) => (
                                        <span key={idx} className="bg-green-500/10 text-green-300 px-3 py-1.5 rounded-full text-sm font-medium border border-green-500/20">
                                            {skill}
                                        </span>
                                    ))}
                                    {(!structuredData.matched_skills && !structuredData.strengths) && (
                                        <span className="text-gray-500 italic">No specific matches found.</span>
                                    )}
                                </div>
                            </div>

                            {/* Missing Skills */}
                            <div className="bg-gray-800 rounded-2xl p-6 border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.1)]">
                                <h3 className="text-xl font-bold text-red-400 mb-6 flex items-center gap-2">
                                    <XCircle size={24} /> Missing Skills
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {(structuredData.missing_skills || structuredData.weaknesses || []).map((skill, idx) => (
                                        <span key={idx} className="bg-red-500/10 text-red-300 px-3 py-1.5 rounded-full text-sm font-medium border border-red-500/20">
                                            {skill}
                                        </span>
                                    ))}
                                    {(!structuredData.missing_skills && !structuredData.weaknesses) && (
                                        <span className="text-gray-500 italic">No critical gaps found.</span>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* 3. Formatting & Structure Analysis */}
                        {(structuredData.formatting_score !== undefined || structuredData.formatting_issues?.length > 0) && (
                            <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700">
                                <h3 className="text-xl font-bold text-orange-400 mb-6 flex items-center gap-2">
                                    <FileText size={24} /> Formatting & Structure
                                </h3>
                                <div className="flex flex-col md:flex-row gap-8 items-center">
                                    {/* Score */}
                                    {structuredData.formatting_score !== undefined && (
                                        <div className="text-center min-w-[150px]">
                                            <div className="text-4xl font-bold text-white mb-2">
                                                {structuredData.formatting_score}/100
                                            </div>
                                            <div className="text-sm text-gray-400">Presentation Score</div>
                                            <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden mt-3">
                                                <div
                                                    className={`h-full ${structuredData.formatting_score >= 80 ? 'bg-green-500' : structuredData.formatting_score >= 60 ? 'bg-orange-500' : 'bg-red-500'}`}
                                                    style={{ width: `${structuredData.formatting_score}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Issues */}
                                    <div className="flex-1 w-full">
                                        <h4 className="text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wider">Identified Issues</h4>
                                        {structuredData.formatting_issues && structuredData.formatting_issues.length > 0 ? (
                                            <div className="grid grid-cols-1 gap-3">
                                                {structuredData.formatting_issues.map((issue, idx) => (
                                                    <div key={idx} className="flex items-start gap-3 bg-orange-900/10 p-3 rounded-lg border border-orange-900/30">
                                                        <AlertCircle className="text-orange-400 shrink-0 mt-0.5" size={16} />
                                                        <span className="text-gray-300 text-sm">{issue}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-2 text-green-400 bg-green-900/10 p-4 rounded-lg border border-green-900/30">
                                                <CheckCircle size={20} />
                                                <span>No major formatting issues detected. Great job!</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* 3. Recommendations */}
                        <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700">
                            <h3 className="text-xl font-bold text-blue-400 mb-6 flex items-center gap-2">
                                <TrendingUp size={24} /> Recommended Learning Path
                            </h3>
                            <div className="space-y-4">
                                {(structuredData.recommendations || structuredData.suggestions || []).map((rec, idx) => (
                                    <div key={idx} className="flex items-start gap-3 p-4 bg-gray-900/30 rounded-xl border border-gray-700/50 hover:border-blue-500/30 transition-colors">
                                        <div className="mt-1 min-w-[24px] flex justify-center">
                                            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-bold">
                                                {idx + 1}
                                            </div>
                                        </div>
                                        <p className="text-gray-300">{rec}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* 4. Job Context & ATS Score */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="md:col-span-2 bg-gray-800 p-6 rounded-2xl border border-gray-700">
                                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <Briefcase size={20} className="text-purple-400" /> Job Context
                                </h3>
                                <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-700/50">
                                    <p className="text-sm text-gray-400 mb-1">Evaluated Against</p>
                                    <p className="text-white font-medium mb-3">{structuredData.job_context?.title || jobRole}</p>
                                    {structuredData.job_context?.requirements_summary && (
                                        <>
                                            <p className="text-sm text-gray-400 mb-1">Key Requirements</p>
                                            <p className="text-gray-300 text-sm">{structuredData.job_context.requirements_summary}</p>
                                        </>
                                    )}
                                </div>
                            </div>

                            <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 text-center flex flex-col items-center justify-center">
                                <div className="text-gray-400 mb-2 font-medium">ATS Compatibility</div>
                                <div className="text-4xl font-bold text-white mb-2">
                                    {structuredData.ats_score || 0}/100
                                </div>
                                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden mt-2">
                                    <div
                                        className="h-full bg-purple-500"
                                        style={{ width: `${structuredData.ats_score || 0}%` }}
                                    ></div>
                                </div>
                                {(structuredData.ats_keywords_missing && structuredData.ats_keywords_missing.length > 0) && (
                                    <p className="text-xs text-red-400 mt-2">Missing {structuredData.ats_keywords_missing.length} keywords</p>
                                )}
                            </div>
                        </div>

                    </div>
                )}
            </div>
        </div>
    );
};

export default Analyzer;
