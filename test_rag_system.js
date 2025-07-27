// Test script to verify the RAG system is working properly
const fetch = require('node-fetch');

async function testRAGSystem() {
    const testCases = [
        {
            name: "Interview Invitation Test",
            subject: "Your resume has been shortlisted",
            content: "Hi Vikas, Your resume has been shortlisted. When will be a good time for you to attend the technical interview?",
            sender: "hr@techcompany.com"
        },
        {
            name: "Job Opportunity Test", 
            subject: "Full Stack Developer Position",
            content: "We have an opening for Full Stack Developer. Are you interested?",
            sender: "recruiter@startup.com"
        },
        {
            name: "Project Collaboration Test",
            subject: "Collaboration Opportunity",
            content: "Would you like to collaborate on an AI project with our team?",
            sender: "founder@aicompany.com"
        }
    ];

    console.log('🧪 Testing RAG System with Enhanced Interview Examples...\n');

    for (const testCase of testCases) {
        console.log(`\n📧 Testing: ${testCase.name}`);
        console.log(`📨 Subject: ${testCase.subject}`);
        console.log(`📝 Content: ${testCase.content}`);
        
        try {
            const response = await fetch('http://localhost:4000/api/suggest-reply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test-token' // We'll test without proper auth
                },
                body: JSON.stringify({
                    emailContent: testCase.content,
                    sender: testCase.sender,
                    subject: testCase.subject
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                console.log(`✅ Generated Reply: ${result.suggestion}`);
                
                // Check if reply contains calendar link for interview-related emails
                if (testCase.name.includes('Interview') || testCase.name.includes('Job')) {
                    const hasCalendarLink = result.suggestion.includes('https://cal.com/vikastg');
                    console.log(`🔗 Contains Calendar Link: ${hasCalendarLink ? '✅ YES' : '❌ NO'}`);
                }
            } else {
                console.log(`❌ Error: ${result.error}`);
            }
        } catch (error) {
            console.log(`❌ Request Failed: ${error.message}`);
        }
        
        console.log('---'.repeat(20));
    }
}

testRAGSystem().catch(console.error);
