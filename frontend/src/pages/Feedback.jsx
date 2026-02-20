import React, { useState } from 'react';
import { MessageSquare, Send, Star, CheckCircle } from 'lucide-react';
import api from '../services/api';

const Feedback = () => {
    const [formData, setFormData] = useState({
        rating: 5,
        usability_score: 5,
        feature_satisfaction: 5,
        missing_features: '',
        improvement_suggestions: '',
        user_experience: ''
    });
    const [submitted, setSubmitted] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleRatingChange = (name, value) => {
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('/feedback/', formData);
            setSubmitted(true);
        } catch (error) {
            console.error("Error submitting feedback:", error);
            alert("Failed to submit feedback. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const renderStars = (name, value) => {
        return (
            <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        type="button"
                        onClick={() => handleRatingChange(name, star)}
                        className={`transition-colors ${star <= value ? 'text-yellow-400' : 'text-gray-600 hover:text-yellow-400/50'}`}
                    >
                        <Star size={24} fill={star <= value ? "currentColor" : "none"} />
                    </button>
                ))}
            </div>
        );
    };

    if (submitted) {
        return (
            <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center px-4">
                <div className="max-w-md w-full bg-gray-800 rounded-2xl p-8 text-center border border-gray-700">
                    <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-6 text-green-500">
                        <CheckCircle size={32} />
                    </div>
                    <h2 className="text-2xl font-bold mb-2">Thank You!</h2>
                    <p className="text-gray-400 mb-6">Your feedback helps us improve Smart Resume AI.</p>
                    <button
                        onClick={() => setSubmitted(false)}
                        className="text-blue-400 hover:text-blue-300 font-medium"
                    >
                        Submit another response
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-pink-500 to-orange-400 bg-clip-text text-transparent mb-4">
                        We Value Your Feedback
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Help us make Smart Resume AI better for everyone
                    </p>
                </div>

                <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 p-8">
                    <form onSubmit={handleSubmit} className="space-y-8">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <div className="space-y-2 text-center md:text-left">
                                <label className="block text-sm font-medium text-gray-300">Overall Rating</label>
                                {renderStars('rating', formData.rating)}
                            </div>
                            <div className="space-y-2 text-center md:text-left">
                                <label className="block text-sm font-medium text-gray-300">Usability</label>
                                {renderStars('usability_score', formData.usability_score)}
                            </div>
                            <div className="space-y-2 text-center md:text-left">
                                <label className="block text-sm font-medium text-gray-300">Features</label>
                                {renderStars('feature_satisfaction', formData.feature_satisfaction)}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Missing Features</label>
                                <textarea
                                    name="missing_features"
                                    value={formData.missing_features}
                                    onChange={handleChange}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none h-24 resize-none"
                                    placeholder="What features would you like to see?"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Improvement Suggestions</label>
                                <textarea
                                    name="improvement_suggestions"
                                    value={formData.improvement_suggestions}
                                    onChange={handleChange}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none h-24 resize-none"
                                    placeholder="How can we improve existing features?"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">User Experience</label>
                                <textarea
                                    name="user_experience"
                                    value={formData.user_experience}
                                    onChange={handleChange}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none h-24 resize-none"
                                    placeholder="Tell us about your experience..."
                                />
                            </div>
                        </div>

                        <div className="flex justify-end pt-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex items-center gap-2 bg-gradient-to-r from-pink-500 to-orange-500 hover:opacity-90 text-white font-bold py-3 px-8 rounded-full transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? "Sending..." : "Submit Feedback"}
                                {!loading && <Send size={18} />}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Feedback;
