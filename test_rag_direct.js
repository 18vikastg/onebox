// Direct test of the RAG functions without API calls
const fs = require('fs');

// Read the index.js file and extract the RAG functions
const indexContent = fs.readFileSync('index.js', 'utf8');

// We'll manually test the RAG functions
console.log('🧪 Testing RAG Functions Directly...\n');

// Extract the RAG training examples (simulated)
const ragTrainingExamples = [
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_invitation',
        input: 'Your resume has been shortlisted. When will be a good time for you to attend the technical interview?',
        output: 'Thank you for shortlisting my profile! I\'m available for a technical interview. You can book a slot here: https://cal.com/vikastg'
    },
    {
        type: 'INTERVIEW_INVITATION',
        scenario: 'interview_invitation', 
        input: 'Hi, Your resume has been shortlisted. When will be a good time for you to attend the technical interview?',
        output: 'Thank you for shortlisting my profile! I\'m available for a technical interview. You can book a slot here: https://cal.com/vikastg'
    },
    {
        type: 'JOB_OPPORTUNITY',
        scenario: 'job_posting',
        input: 'We have an opening for Full Stack Developer. Are you interested?',
        output: 'Thank you for reaching out! I\'m very interested in the Full Stack Developer position. I have experience with React, Node.js, and Python. Could you share more details about the role? My portfolio: https://vikastg.vercel.app'
    }
];

// Simulated retrieveRelevantExamples function
function retrieveRelevantExamples(emailContent, subject) {
    const normalizedContent = emailContent.toLowerCase();
    const normalizedSubject = (subject || '').toLowerCase();
    const combinedText = `${normalizedSubject} ${normalizedContent}`;
    
    console.log('🔍 RAG Analysis - Subject:', subject);
    console.log('🔍 RAG Analysis - Content snippet:', emailContent.substring(0, 100));
    
    // Score each example based on relevance
    const scoredExamples = ragTrainingExamples.map(example => {
        let score = 0;
        const exampleInput = example.input.toLowerCase();
        const exampleScenario = example.scenario.toLowerCase();
        
        // Enhanced keyword matching with better patterns
        const keyPatterns = [
            { pattern: /(interview|shortlist|select|technical|round|schedule|time)/g, boost: 10, type: 'INTERVIEW' },
            { pattern: /(job|position|role|opportunity|hiring|career|apply|opening|developer|engineer)/g, boost: 8, type: 'JOB' },
            { pattern: /(project|collaboration|work|team|development)/g, boost: 6, type: 'PROJECT' },
            { pattern: /(calendar|book|slot|available|time|meeting)/g, boost: 8, type: 'SCHEDULING' }
        ];
        
        // Check patterns in both email content and examples
        keyPatterns.forEach(pattern => {
            const emailMatches = (combinedText.match(pattern.pattern) || []).length;
            const exampleMatches = (exampleInput.match(pattern.pattern) || []).length;
            
            if (emailMatches > 0 && exampleMatches > 0) {
                score += pattern.boost * Math.min(emailMatches, 3);
            }
        });
        
        // Direct type matching
        if (example.type === 'INTERVIEW_INVITATION' && 
            (combinedText.includes('interview') || combinedText.includes('shortlist'))) {
            score += 20;
        }
        
        if (example.type === 'JOB_OPPORTUNITY' && 
            (combinedText.includes('job') || combinedText.includes('opening') || 
             combinedText.includes('position') || combinedText.includes('developer'))) {
            score += 15;
        }
        
        console.log(`📊 Example "${example.scenario}" scored: ${score}`);
        return { ...example, score };
    });
    
    // Return top 2 most relevant examples
    const topExamples = scoredExamples
        .sort((a, b) => b.score - a.score)
        .slice(0, 2)
        .filter(example => example.score > 0);
    
    console.log('🎯 Selected examples:', topExamples.map(ex => `${ex.scenario} (${ex.score})`));
    return topExamples;
}

// Test cases
const testCases = [
    {
        name: "Interview Invitation Test",
        subject: "Your resume has been shortlisted",
        content: "Hi Vikas, Your resume has been shortlisted. When will be a good time for you to attend the technical interview?",
    },
    {
        name: "Job Opportunity Test", 
        subject: "Full Stack Developer Position",
        content: "We have an opening for Full Stack Developer. Are you interested?",
    },
    {
        name: "General Inquiry Test",
        subject: "Hello",
        content: "Just wanted to say hello and see how you're doing.",
    }
];

console.log('='.repeat(60));
for (const testCase of testCases) {
    console.log(`\n📧 Testing: ${testCase.name}`);
    console.log(`📨 Subject: ${testCase.subject}`);
    console.log(`📝 Content: ${testCase.content}`);
    console.log('-'.repeat(40));
    
    const relevantExamples = retrieveRelevantExamples(testCase.content, testCase.subject);
    
    if (relevantExamples.length > 0) {
        console.log('✅ RAG System Found Relevant Examples:');
        relevantExamples.forEach((example, index) => {
            console.log(`   ${index + 1}. Type: ${example.type}`);
            console.log(`      Scenario: ${example.scenario}`);
            console.log(`      Score: ${example.score}`);
            console.log(`      Expected Output: ${example.output.substring(0, 100)}...`);
        });
        
        // Check if interview-related content gets calendar link
        const hasInterviewExample = relevantExamples.some(ex => 
            ex.type === 'INTERVIEW_INVITATION' || 
            ex.output.includes('https://cal.com/vikastg')
        );
        console.log(`🔗 Will include calendar link: ${hasInterviewExample ? '✅ YES' : '❌ NO'}`);
    } else {
        console.log('❌ No relevant examples found');
    }
    
    console.log('='.repeat(60));
}
