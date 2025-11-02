import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { FileText, ClipboardList, CheckCircle, XCircle, Zap, Loader2, Upload } from 'lucide-react';

// --- Utility Components for Visuals ---

/**
 * Animated Radial Match Score Display
 */
const MatchScoreCard = ({ score, isLoading }) => {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color = score >= 70 ? 'text-green-500' : score >= 50 ? 'text-yellow-500' : 'text-red-500';
  const fill = score >= 70 ? 'rgb(22 163 74 / 0.1)' : score >= 50 ? 'rgb(245 158 11 / 0.1)' : 'rgb(239 68 68 / 0.1)';

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg transition duration-300">
      <h3 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">Match Score</h3>
      <div className="relative h-36 w-36">
        <svg className="h-full w-full transform -rotate-90" viewBox="0 0 140 140">
          {/* Background Circle */}
          <circle
            className="text-gray-200 dark:text-gray-700"
            strokeWidth="10"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="70"
            cy="70"
          />
          {/* Progress Circle */}
          <circle
            className={`${color} transition-all duration-1000 ease-in-out`}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            stroke="currentColor"
            fill={fill}
            r={radius}
            cx="70"
            cy="70"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          {isLoading ? (
            <Loader2 className="h-10 w-10 text-indigo-500 animate-spin" />
          ) : (
            <span className={`text-4xl font-extrabold ${color}`}>{score}%</span>
          )}
        </div>
      </div>
      <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
        {isLoading ? 'Analyzing...' : `Alignment: ${score}%`}
      </p>
    </div>
  );
};

/**
 * Display for Matched and Missing Skills
 */
const MatchDetail = ({ title, items, icon: Icon, color, className }) => (
  <div className={`p-6 rounded-xl border ${color} bg-white dark:bg-gray-800 shadow-md ${className}`}>
    <h3 className="text-lg font-semibold flex items-center mb-4 text-gray-800 dark:text-gray-100">
      <Icon className={`w-5 h-5 mr-2 ${color.replace('border-', 'text-')}`} />
      {title} ({items.length})
    </h3>
    <ul className="space-y-2 max-h-64 overflow-y-auto pr-2">
      {items.map((item, index) => (
        <li key={index} className="flex items-center text-sm text-gray-600 dark:text-gray-300">
          <span className={`inline-block w-2 h-2 mr-2 rounded-full ${color.replace('border-', 'bg-')}`}></span>
          {item}
        </li>
      ))}
      {items.length === 0 && (
        <li className="text-sm italic text-gray-400 dark:text-gray-500">No items found in this category.</li>
      )}
    </ul>
  </div>
);

// --- Custom Hook for Logic Encapsulation ---

// Endpoint for final match calculation
const BACKEND_MATCH_URL = process.env.REACT_APP_BACKEND_URL + process.env.REACT_APP_BACKEND_MATCH_PATH;
// NEW Endpoint for text extraction from binary files (PDF/DOCX)
const BACKEND_EXTRACT_URL = process.env.REACT_APP_BACKEND_URL + process.env.REACT_APP_BACKEND_EXTRACT_PATH;
console.log(BACKEND_EXTRACT_URL)

const useMatcher = () => {
  const [resumeText, setResumeText] = useState('');
  const [jdText, setJdText] = useState('');
  const [matchResult, setMatchResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false); // NEW state for extraction loading
  const [errorMessage, setErrorMessage] = useState('');
  const [resumeFileName, setResumeFileName] = useState('');
  const [jdFileName, setJdFileName] = useState('');

  // STATE: Store file data (Base64 + MIME type) for API processing
  const [resumeFileData, setResumeFileData] = useState(null);
  const [jdFileData, setJdFileData] = useState(null);

  // Initial placeholder content
  useEffect(() => {
    setResumeText(
//       `Experienced professional skilled in Agile, User Stories, medical, Stakeholder Management. 
// They likely much way. 
// Final ball cause meet describe.
//   `
`Experienced professional skilled in book, SQL, word, Tableau, realize, Data Cleaning. 
Three purpose safe develop. 
Research none carry fire wrong.`
    );
    setJdText(
//       `Product Manager needed with experience in Scrum, Product Roadmap, User Stories, Stakeholder Management, Agile. 
// Either thank entire unit nor. 
// Yourself source experience a finally hope. Close while food there can.`
`Data Analyst needed with experience in Tableau, Power BI, Reporting, Excel. 
Option conference win coach military offer. 
Well home improve expect.`
    );
  }, []);

  const clearInput = useCallback((type) => {
    if (type === 'resume') {
      setResumeText('');
      setResumeFileName('');
      setResumeFileData(null); // Clear file data
    } else if (type === 'jd') {
      setJdText('');
      setJdFileName('');
      setJdFileData(null); // Clear file data
    }
  }, []);

  /**
   * Function to call the backend to extract text from a binary file (PDF/DOCX)
   * and update the main text state.
   */
  const extractTextFromBackend = useCallback(async (fileData, type, fileName, setText, setFileData, setFileName) => {
    if (!fileData) return;

    setIsExtracting(true);
    setText(`Extracting Text from ${fileName} (${fileData.mimeType})... Please wait.`);
    setErrorMessage('');

    try {
      const payload = {
        // file: {
        //   data: fileData.base64,
        //   mimeType: fileData.mimeType,
        // },
        filename: fileName,
        filetype: fileData.fileExtension,
        base64_content: fileData.base64


      };
      console.log(payload)

      const response = await fetch(BACKEND_EXTRACT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Extraction service failed (${response.status}).`);
      }

      const result = await response.json();

      if (result && typeof result.extracted_text === 'string') {
        // SUCCESS: Update text state, clear file data, and enable editing
        setText(result.extracted_text);
        setFileData(null); // Extracted text is now in the main text state
        setErrorMessage(`Text successfully extracted from ${fileName}.`);
      } else {
        throw new Error("Extraction service returned an invalid response.");
      }

    } catch (error) {
      // FAILURE: Keep file data (for match submission) and show error
      setFileData(fileData);
      setText(`--- TEXT EXTRACTION FAILED ---\n\nCould not extract text from ${fileName} on the frontend: ${error.message}.\n\nClick "Calculate Match Score" to submit the file's raw data for backend extraction during the matching process.`);
      setErrorMessage(`Extraction Failed: ${error.message}. Raw file data retained for final match calculation.`);
      setFileName(fileName); // Re-set file name after error
    } finally {
      setIsExtracting(false);
    }
  }, []);


  const handleFileUpload = useCallback((e, type) => {
    setErrorMessage('');
    const file = e.target.files[0];
    if (!file) return;

    const fileName = file.name;
    const mimeType = file.type;
    const fileExtension = fileName.split('.').pop().toLowerCase();

    // Determine the setter functions
    const setText = type === 'resume' ? setResumeText : setJdText;
    const setFileName = type === 'resume' ? setResumeFileName : setJdFileName;
    const setFileData = type === 'resume' ? setResumeFileData : setJdFileData;

    setFileName(fileName);
    setText(''); // Clear text when uploading a new file
    setFileData(null); // Clear previous file data

    const reader = new FileReader();

    reader.onload = (event) => {
      const result = event.target.result;

      if (fileExtension === 'txt') {
        // For TXT, we read the text directly
        setText(result);
        setFileData(null);
      } else if (['pdf', 'docx', 'doc'].includes(fileExtension)) {
        // For PDF/DOCX, store Base64 data and immediately attempt extraction
        const base64Data = result.split(',')[1];
        const fileData = { base64: base64Data, mimeType, fileExtension };
        setFileData(fileData); // Temporarily store while extracting

        // Initiate backend extraction
        extractTextFromBackend(fileData, type, fileName, setText, setFileData, setFileName);

      } else {
        setErrorMessage(`Unsupported file type: ".${fileExtension}". Please use .txt, .pdf, or .docx.`);
      }
    };

    reader.onerror = () => {
      setErrorMessage(`Error reading the file: ${fileName}.`);
    };

    if (fileExtension === 'txt') {
      reader.readAsText(file);
    } else if (['pdf', 'docx', 'doc'].includes(fileExtension)) {
      // Read as Data URL to get Base64 string for multimodal processing
      reader.readAsDataURL(file);
    } else {
      setErrorMessage(`Unsupported file type: ".${fileExtension}". Please use .txt, .pdf, or .docx.`);
    }

  }, [extractTextFromBackend]);


  /**
   * Final matching logic using a Backend service call.
   */
  const calculateMatch = useCallback(async () => {
    setErrorMessage('');
    setMatchResult(null);

    // 1. Determine final content source
    // If file data exists, use it (failed extraction), otherwise use text area content (successful extraction or manual paste).
    const isResumeReady = resumeText.trim() !== '' || resumeFileData !== null;
    const isJdReady = jdText.trim() !== '' || jdFileData !== null;

    if (!isResumeReady || !isJdReady) {
      setErrorMessage("Please provide both Resume and Job Description content (text or file) to calculate the match.");
      return;
    }

    if (isExtracting) {
      setErrorMessage("Please wait for the current text extraction to finish before calculating the match.");
      return;
    }

    setIsLoading(true);

    try {
      // 2. Build the Payload for the Backend Service
      // Send file data if present (extraction failed/skipped), otherwise send plain text.
      const payload = {
        // resume: resumeFileData
        //   ? { type: 'file', data: resumeFileData.base64, mimeType: resumeFileData.mimeType }
        //   : { type: 'text', data: resumeText },

        // job_description: jdFileData
        //   ? { type: 'file', data: jdFileData.base64, mimeType: jdFileData.mimeType }
        //   : { type: 'text', data: jdText }
        resume: resumeText,
        job_description: jdText
      };

      // 3. Call the Backend Service
      const response = await fetch(BACKEND_MATCH_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Backend match service failed: ${response.status}. Details: ${errorText.substring(0, 100)}...`);
      }

      // 4. Process the Backend Result (expecting the final JSON structure: {score, matched, missing})
      const parsedJson = await response.json();

      // 5. Validate structure
      if (typeof parsedJson.score !== 'number') {
        //  || !Array.isArray(parsedJson.matched) || !Array.isArray(parsedJson.missing)) {
        throw new Error("Invalid structure returned by the backend service. Expected {score: number, matched: array, missing: array}.");
      }
      console.log(parsedJson)
      const finalScore = Math.round(parsedJson.score);

      setMatchResult({
        score: finalScore,
        // matched: parsedJson.matched,
        // missing: parsedJson.missing,
        reasoning: parsedJson.reasoning,
      });

    } catch (error) {
      console.error("Backend Match Error:", error);
      setErrorMessage(`Match Calculation Failed: ${error.message}. Please ensure your backend services are running and correctly responding.`);
    } finally {
      setIsLoading(false);
    }
  }, [resumeText, jdText, resumeFileData, jdFileData, isExtracting]);


  return {
    resumeText, setResumeText,
    jdText, setJdText,
    matchResult,
    isLoading,
    isExtracting, // Exporting extraction state
    errorMessage,
    calculateMatch,
    handleFileUpload,
    clearInput,
    resumeFileName,
    jdFileName,
    resumeFileData,
    jdFileData,
  };
};


// --- Main Application Component ---

/**
 * Renders the Score Card, including the backend reasoning.
 * Assuming matchResult exists when this is rendered.
 * @param {MatchResult} matchResult
 */
// const ScoreCard = ({ matchResult }) => {
//     const score = matchResult?.score || 0;
//     const color = score > 75 ? "bg-green-100 text-green-700" : 
//                   score > 50 ? "bg-yellow-100 text-yellow-700" : 
//                                "bg-red-100 text-red-700";
//     const icon = score > 75 ? TrendingUp : BarChart3;

//     return (
//         <div className="p-6 bg-white dark:bg-gray-700 rounded-xl shadow-lg border-t-4 border-indigo-500 h-full flex flex-col">
//             <div className="flex justify-between items-center mb-4">
//                 <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
//                     <BarChart3 className="w-5 h-5 mr-2 text-indigo-500" />
//                     Overall Match Score
//                 </h3>
//                 <div className={`text-3xl font-extrabold p-2 rounded-lg ${color}`}>
//                     {score}%
//                 </div>
//             </div>

//             <h4 className="text-lg font-medium text-gray-700 dark:text-gray-200 mt-4 border-t pt-3">Scoring Reasoning:</h4>
//             <p className="text-gray-600 dark:text-gray-300 text-sm mt-1 flex-grow">
//                 {matchResult?.reasoning || "Reasoning not provided by backend."}
//             </p>
//         </div>
//     );
// };

const MatchReasoning = ({ reasoning }) => (
  <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-indigo-200 dark:border-indigo-700">
    <h3 className="text-lg font-semibold flex items-center mb-3 text-indigo-700 dark:text-indigo-300">
      {/* <Zap className="w-5 h-5 mr-2" /> */}
      AI Scoring Rationale
    </h3>
    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
      {reasoning}
    </p>
  </div>
);


const App = () => {
  const {
    resumeText, setResumeText,
    jdText, setJdText,
    matchResult,
    isLoading,
    isExtracting,
    errorMessage,
    calculateMatch,
    handleFileUpload,
    clearInput,
    resumeFileName,
    jdFileName,
    resumeFileData,
    jdFileData,
  } = useMatcher();

  // Use Memo to prevent re-rendering MatchScoreCard when inputs change but match hasn't been re-run
  const scoreCard = useMemo(() => {
    if (!matchResult && !isLoading) return null;
    return <MatchScoreCard score={matchResult?.score || 0} isLoading={isLoading} />;
  }, [matchResult, isLoading]);

  // Determine if the specific input box is currently extracting or holding binary data
  const isResumeExtracting = isExtracting && resumeFileData !== null;
  const isJDExtracting = isExtracting && jdFileData !== null;
  const isResumeBinaryLoaded = resumeFileData !== null;
  const isJDBinaryLoaded = jdFileData !== null;
  const isAnyInputExtracting = isResumeExtracting || isJDExtracting;


  // Input box component
  const InputBox = ({ type, title, text, setText, fileName, onFileUpload, onClear, isExtractingState, isBinaryLoaded }) => {

    // Text area is read-only if extracting or if it holds failed/raw binary data
    const isReadOnly = isExtractingState || isBinaryLoaded;

    // Visual indicator for read-only state
    const textareaClasses = isReadOnly
      ? 'bg-gray-100 dark:bg-gray-600 border-gray-400 dark:border-gray-500 cursor-default text-gray-600 dark:text-gray-300 italic'
      : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100';

    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg h-[400px] md:h-[600px] flex flex-col">
        <label htmlFor={type} className="flex items-center text-lg font-medium mb-3 text-gray-700 dark:text-gray-200">
          {type === 'resume' ? <FileText className="w-5 h-5 mr-2 text-indigo-500" /> : <ClipboardList className="w-5 h-5 mr-2 text-indigo-500" />}
          {title}
        </label>

        {/* File Upload Section */}
        <div className="flex space-x-2 mb-4">
          <label
            className={`cursor-pointer flex items-center px-4 py-2 text-sm font-medium rounded-lg transition duration-150 ${isAnyInputExtracting ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-indigo-50 border border-indigo-200 text-indigo-600 hover:bg-indigo-100'}`}
          >
            {isExtractingState ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Upload File
              </>
            )}
            <input
              type="file"
              accept=".txt, .pdf, .doc, .docx"
              className="hidden"
              onChange={(e) => onFileUpload(e, type)}
              onClick={(e) => e.target.value = null}
              disabled={isAnyInputExtracting}
            />
          </label>
          <button
            onClick={() => onClear(type)}
            disabled={isAnyInputExtracting}
            className="px-4 py-2 bg-gray-100 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 disabled:bg-gray-200 disabled:text-gray-500 transition duration-150"
          >
            Clear Text
          </button>
        </div>

        <p className="text-sm mb-3 text-gray-500 dark:text-gray-400 truncate">
          {fileName ? `Source: ${fileName}` : 'Paste content or upload a file (TXT, PDF, DOCX).'}
        </p>

        <textarea
          id={type}
          className={`w-full flex-grow p-4 border rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm resize-none transition-colors duration-300 ${textareaClasses}`}
          placeholder={`Paste the plain text content of your ${type} here...`}
          value={text}
          onChange={(e) => setText(e.target.value)}
          readOnly={isReadOnly}
        ></textarea>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 sm:p-8 font-sans transition-colors duration-300">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
          {/* <Zap className="w-8 h-8 mr-2" /> */}
          AI Resume Matcher
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Instantly compare your resume against a job description to find keyword alignment and skill gaps.
        </p>
      </header>

      <div className="max-w-7xl mx-auto">

        {/* Error Message Display */}
        {errorMessage && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-center font-medium dark:bg-red-900 dark:border-red-700 dark:text-red-300">
            {errorMessage}
          </div>
        )}

        {/* Input and Action Section */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Resume Input */}
          <InputBox
            type="resume"
            title="Resume Text Source"
            text={resumeText}
            setText={setResumeText}
            fileName={resumeFileName}
            onFileUpload={handleFileUpload}
            onClear={clearInput}
            isExtractingState={isResumeExtracting}
            isBinaryLoaded={isResumeBinaryLoaded}
          />

          {/* JD Input */}
          <InputBox
            type="jd"
            title="Job Description Text Source"
            text={jdText}
            setText={setJdText}
            fileName={jdFileName}
            onFileUpload={handleFileUpload}
            onClear={clearInput}
            isExtractingState={isJDExtracting}
            isBinaryLoaded={isJDBinaryLoaded}
          />
        </div>

        {/* Match Button */}
        <div className="flex justify-center mb-12">
          <button
            onClick={calculateMatch}
            // Disable if loading match, extracting, or both inputs are empty
            disabled={isLoading || isAnyInputExtracting || (!resumeText && !jdText && !resumeFileName && !jdFileName)}
            className="flex items-center px-8 py-3 text-lg font-bold text-white bg-indigo-600 rounded-full shadow-xl hover:bg-indigo-700 disabled:bg-indigo-400 disabled:cursor-not-allowed transition duration-300 transform hover:scale-[1.02] active:scale-[0.98]"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Matching...
              </>
            ) : isAnyInputExtracting ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Wait for Extraction...
              </>
            ) : (
              <>
                {/* <Zap className="w-5 h-5 mr-2" /> */}
                Calculate Match Score ✨
              </>
            )}
          </button>
        </div>

        {/* Results Section */}
        {(matchResult || isLoading) && (
          <div className="p-8 bg-indigo-50 dark:bg-gray-800 rounded-xl shadow-2xl">
            <h2 className="text-2xl font-bold mb-6 text-indigo-700 dark:text-indigo-300 border-b pb-2 border-indigo-200 dark:border-gray-700">
              Analysis Results
            </h2>

            <div className="grid md:grid-cols-3 gap-6">
              {/* Score Card (Always visible when result or loading) */}
              <div className="md:col-span-1">
                {scoreCard}
              </div>
              {/* Bottom Row: AI Reasoning (New section) */}
              {matchResult && matchResult.reasoning && (
                <div className="lg:col-span-2">
                  {/* The MatchReasoning component has been internally updated to fill height and handle scrolling */}
                  <MatchReasoning reasoning={matchResult.reasoning} />
                </div>
              )}


              {/* Matched and Missing Skills (Only visible after result is calculated) */}
              {/* {matchResult && (
                <>
                  <MatchDetail
                    title="Matched Core Skills"
                    items={matchResult.matched}
                    icon={CheckCircle}
                    color="border-green-500"
                    className="md:col-span-1"
                  />
                  <MatchDetail
                    title="Missing Critical Skills"
                    items={matchResult.missing}
                    icon={XCircle}
                    color="border-red-500"
                    className="md:col-span-1"
                  />
                </>
              )} */}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
