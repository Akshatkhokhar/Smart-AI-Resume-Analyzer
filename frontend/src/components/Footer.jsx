import React from 'react';
import { Heart } from 'lucide-react';

const Footer = () => {
    return (
        <footer className="bg-gray-900 border-t border-gray-800 py-6 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <div className="text-gray-400 text-sm">
                        © {new Date().getFullYear()} Smart AI Resume Analyzer. All rights reserved.
                    </div>
                    <div className="flex items-center gap-1 text-gray-400 text-sm mt-2 md:mt-0">
                        <span>Made with</span>
                        <Heart size={16} className="text-red-500 fill-current" />
                        <span>by Smart Resume AI Team</span>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
