import React, { useState } from 'react';
import { Plus, Trash2, Download, FileText, Briefcase, GraduationCap, Code, User, ChevronRight, ChevronLeft } from 'lucide-react';
import api from '../services/api';

const ResumeBuilder = () => {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    const [formData, setFormData] = useState({
        fullName: '',
        email: '',
        phone: '',
        location: '',
        linkedin: '',
        summary: '',
        experience: [],
        education: [],
        skills: '',
        projects: []
    });

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    // Experience Handlers
    const addExperience = () => {
        setFormData(prev => ({
            ...prev,
            experience: [...prev.experience, { title: '', company: '', startDate: '', endDate: '', description: '' }]
        }));
    };

    const updateExperience = (index, field, value) => {
        const newExp = [...formData.experience];
        newExp[index][field] = value;
        setFormData(prev => ({ ...prev, experience: newExp }));
    };

    const removeExperience = (index) => {
        const newExp = formData.experience.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, experience: newExp }));
    };

    // Education Handlers
    const addEducation = () => {
        setFormData(prev => ({
            ...prev,
            education: [...prev.education, { school: '', degree: '', year: '' }]
        }));
    };

    const updateEducation = (index, field, value) => {
        const newEdu = [...formData.education];
        newEdu[index][field] = value;
        setFormData(prev => ({ ...prev, education: newEdu }));
    };

    const removeEducation = (index) => {
        const newEdu = formData.education.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, education: newEdu }));
    };

    // Project Handlers
    const addProject = () => {
        setFormData(prev => ({
            ...prev,
            projects: [...prev.projects, { name: '', description: '' }]
        }));
    };

    const updateProject = (index, field, value) => {
        const newProj = [...formData.projects];
        newProj[index][field] = value;
        setFormData(prev => ({ ...prev, projects: newProj }));
    };

    const removeProject = (index) => {
        const newProj = formData.projects.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, projects: newProj }));
    };

    const generatePDF = async () => {
        setLoading(true);
        try {
            const response = await api.post('/builder/generate', formData, {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${formData.fullName.replace(/\s+/g, '_')}_Resume.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Error generating PDF:", error);
            alert("Failed to generate resume. Please check your inputs.");
        } finally {
            setLoading(false);
        }
    };

    const renderStep1_Personal = () => (
        <div className="space-y-4 animate-fadeIn">
            <h2 className="text-2xl font-bold text-blue-400 mb-6 flex items-center gap-2">
                <User /> Personal Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-gray-400 mb-1">Full Name <span className="text-red-500">*</span></label>
                    <input
                        type="text"
                        value={formData.fullName}
                        onChange={(e) => handleInputChange('fullName', e.target.value)}
                        className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Email <span className="text-red-500">*</span></label>
                    <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Phone</label>
                    <input
                        type="text"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div>
                    <label className="block text-gray-400 mb-1">Location</label>
                    <input
                        type="text"
                        value={formData.location}
                        onChange={(e) => handleInputChange('location', e.target.value)}
                        className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div className="col-span-1 md:col-span-2">
                    <label className="block text-gray-400 mb-1">LinkedIn URL</label>
                    <input
                        type="text"
                        value={formData.linkedin}
                        onChange={(e) => handleInputChange('linkedin', e.target.value)}
                        className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div className="col-span-1 md:col-span-2">
                    <label className="block text-gray-400 mb-1">Professional Summary</label>
                    <textarea
                        value={formData.summary}
                        onChange={(e) => handleInputChange('summary', e.target.value)}
                        rows="4"
                        className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
            </div>
        </div>
    );

    const renderStep2_Experience = () => (
        <div className="space-y-6 animate-fadeIn">
            <h2 className="text-2xl font-bold text-blue-400 mb-6 flex items-center gap-2">
                <Briefcase /> Experience
            </h2>
            {formData.experience.map((exp, index) => (
                <div key={index} className="bg-gray-800 p-4 rounded-lg relative border border-gray-700">
                    <button
                        onClick={() => removeExperience(index)}
                        className="absolute top-2 right-2 text-red-400 hover:text-red-300"
                    >
                        <Trash2 size={20} />
                    </button>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-gray-400 mb-1">Job Title <span className="text-red-500">*</span></label>
                            <input
                                type="text"
                                value={exp.title}
                                onChange={(e) => updateExperience(index, 'title', e.target.value)}
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-400 mb-1">Company <span className="text-red-500">*</span></label>
                            <input
                                type="text"
                                value={exp.company}
                                onChange={(e) => updateExperience(index, 'company', e.target.value)}
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-400 mb-1">Start Date</label>
                            <input
                                type="text"
                                value={exp.startDate}
                                onChange={(e) => updateExperience(index, 'startDate', e.target.value)}
                                placeholder="e.g. Jan 2020"
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-400 mb-1">End Date</label>
                            <input
                                type="text"
                                value={exp.endDate}
                                onChange={(e) => updateExperience(index, 'endDate', e.target.value)}
                                placeholder="e.g. Present"
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                        <div className="col-span-1 md:col-span-2">
                            <label className="block text-gray-400 mb-1">Description</label>
                            <textarea
                                value={exp.description}
                                onChange={(e) => updateExperience(index, 'description', e.target.value)}
                                rows="3"
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                    </div>
                </div>
            ))}
            <button
                onClick={addExperience}
                className="flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium"
            >
                <Plus size={20} /> Add Experience
            </button>
        </div>
    );

    const renderStep3_Education = () => (
        <div className="space-y-6 animate-fadeIn">
            <h2 className="text-2xl font-bold text-blue-400 mb-6 flex items-center gap-2">
                <GraduationCap /> Education
            </h2>
            {formData.education.map((edu, index) => (
                <div key={index} className="bg-gray-800 p-4 rounded-lg relative border border-gray-700">
                    <button
                        onClick={() => removeEducation(index)}
                        className="absolute top-2 right-2 text-red-400 hover:text-red-300"
                    >
                        <Trash2 size={20} />
                    </button>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-gray-400 mb-1">School/University <span className="text-red-500">*</span></label>
                            <input
                                type="text"
                                value={edu.school}
                                onChange={(e) => updateEducation(index, 'school', e.target.value)}
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-400 mb-1">Degree</label>
                            <input
                                type="text"
                                value={edu.degree}
                                onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-400 mb-1">Year</label>
                            <input
                                type="text"
                                value={edu.year}
                                onChange={(e) => updateEducation(index, 'year', e.target.value)}
                                className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                            />
                        </div>
                    </div>
                </div>
            ))}
            <button
                onClick={addEducation}
                className="flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium"
            >
                <Plus size={20} /> Add Education
            </button>
        </div>
    );

    const renderStep4_SkillsProjects = () => (
        <div className="space-y-6 animate-fadeIn">
            <h2 className="text-2xl font-bold text-blue-400 mb-6 flex items-center gap-2">
                <Code /> Skills & Projects
            </h2>

            <div className="mb-8">
                <label className="block text-gray-400 mb-2">Skills (Comma separated) <span className="text-red-500">*</span></label>
                <textarea
                    value={formData.skills}
                    onChange={(e) => handleInputChange('skills', e.target.value)}
                    rows="3"
                    placeholder="e.g. React, Python, JavaScript, Leadership"
                    className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
            </div>

            <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-300">Projects</h3>
                {formData.projects.map((proj, index) => (
                    <div key={index} className="bg-gray-800 p-4 rounded-lg relative border border-gray-700">
                        <button
                            onClick={() => removeProject(index)}
                            className="absolute top-2 right-2 text-red-400 hover:text-red-300"
                        >
                            <Trash2 size={20} />
                        </button>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-gray-400 mb-1">Project Name <span className="text-red-500">*</span></label>
                                <input
                                    type="text"
                                    value={proj.name}
                                    onChange={(e) => updateProject(index, 'name', e.target.value)}
                                    className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-gray-400 mb-1">Description</label>
                                <textarea
                                    value={proj.description}
                                    onChange={(e) => updateProject(index, 'description', e.target.value)}
                                    rows="2"
                                    className="w-full bg-gray-700 rounded-lg p-2 text-white outline-none"
                                />
                            </div>
                        </div>
                    </div>
                ))}
                <button
                    onClick={addProject}
                    className="flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium"
                >
                    <Plus size={20} /> Add Project
                </button>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent mb-4">
                        Resume Builder
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Create a professional resume in minutes
                    </p>
                </div>

                {/* Progress Bar */}
                <div className="mb-8 bg-gray-800 rounded-full h-2.5">
                    <div
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${(step / 4) * 100}%` }}
                    ></div>
                </div>

                <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-8 mb-8">
                    {step === 1 && renderStep1_Personal()}
                    {step === 2 && renderStep2_Experience()}
                    {step === 3 && renderStep3_Education()}
                    {step === 4 && renderStep4_SkillsProjects()}

                    <div className="flex justify-between mt-8 pt-6 border-t border-gray-700">
                        {step > 1 ? (
                            <button
                                onClick={() => setStep(step - 1)}
                                className="flex items-center gap-2 text-gray-300 hover:text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition"
                            >
                                <ChevronLeft /> Back
                            </button>
                        ) : <div></div>}

                        {step < 4 ? (
                            <button
                                onClick={() => setStep(step + 1)}
                                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition"
                            >
                                Next <ChevronRight />
                            </button>
                        ) : (
                            <button
                                onClick={generatePDF}
                                disabled={loading}
                                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-bold transition transform hover:scale-105"
                            >
                                {loading ? "Generating..." : "Download Resume PDF"} <Download size={20} />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResumeBuilder;
