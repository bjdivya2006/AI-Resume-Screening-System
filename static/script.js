document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("screeningForm");
    const jobRole = document.getElementById("job_role");
    const resumeInput = document.getElementById("resumes");
    const selectedFiles = document.getElementById("selectedFiles");
    const analyzeButton = document.getElementById("analyzeBtn");
    const loading = document.getElementById("loading");
    const resultsSection = document.getElementById("resultsSection");
    const results = document.getElementById("results");
    let selectedResumeFiles = [];
    resumeInput.addEventListener("change", function () {
        const newFiles = Array.from(this.files);
        newFiles.forEach(file => {
            const fileName = file.name.toLowerCase();
            if (
                !fileName.endsWith(".pdf") &&
                !fileName.endsWith(".docx")
            ) {
                alert(
                    `"${file.name}" is not supported.\n\n` +
                    "Please upload PDF or DOCX files."
                );
                return;
            }
            const duplicate =
                selectedResumeFiles.some(existingFile =>
                    existingFile.name === file.name &&
                    existingFile.size === file.size
                );
            if (!duplicate) {
                selectedResumeFiles.push(file);
            }
        });
        updateFileList();
        this.value = "";
    });
    function updateFileList() {
        selectedFiles.innerHTML = "";
        if (selectedResumeFiles.length === 0) {
            selectedFiles.innerHTML = `
                <p class="no-files">
                    No resumes selected.
                </p>
            `;
            return;
        }
        const heading =
            document.createElement("div");
        heading.className =
            "file-count";
        heading.innerHTML = `
            <strong>
                ${selectedResumeFiles.length}
            </strong>
            resume${selectedResumeFiles.length === 1 ? "" : "s"}
            selected
        `;
        selectedFiles.appendChild(heading);
        selectedResumeFiles.forEach(
            (file, index) => {
                const fileItem =
                    document.createElement("div");
                fileItem.className =
                    "file-item";
                fileItem.innerHTML = `
                    <span class="file-name">
                        📄
                        ${escapeHTML(file.name)}
                        <small>
                            (${formatFileSize(file.size)})
                        </small>
                    </span>
                    <button
                        type="button"
                        class="remove-file"
                        data-index="${index}"
                    >
                        ✕
                    </button>
                `;
                selectedFiles.appendChild(fileItem);
            }
        );
        document
            .querySelectorAll(".remove-file")
            .forEach(button => {
                button.addEventListener(
                    "click",
                    function () {
                        const index =
                            Number(this.dataset.index);
                        selectedResumeFiles.splice(
                            index,
                            1
                        );
                        updateFileList();
                    }
                );
            });
    }
    form.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();
            const vacancy =
                jobRole.value.trim();
            if (!vacancy) {
                alert(
                    "Please enter the vacancy/job role.\n\n" +
                    "Example: Java Developer"
                );
                jobRole.focus();
                return;
            }
            if (selectedResumeFiles.length === 0) {
                alert(
                    "Please upload at least one resume."
                );
                return;
            }
            const formData =
                new FormData();
            formData.append(
                "job_role",
                vacancy
            );
            selectedResumeFiles.forEach(file => {
                formData.append(
                    "resumes",
                    file,
                    file.name
                );
            });
            setLoading(true);
            resultsSection.style.display =
                "none";
            try {
                const response =
                    await fetch(
                        "/screen",
                        {
                            method: "POST",
                            body: formData
                        }
                    );
                const data =
                    await response.json();
                console.log(
                    "Screening result:",
                    data
                );
                if (!response.ok) {
                    throw new Error(
                        data.error ||
                        "Resume screening failed."
                    );
                }
                displayResults(data);
            } catch (error) {
                console.error(error);
                alert(
                    "Analysis failed.\n\n" +
                    error.message
                );
            } finally {
                setLoading(false);
            }
        }
    );
    function setLoading(state) {
        if (state) {
            analyzeButton.disabled = true;
            analyzeButton.textContent =
                "⏳ Analyzing Resumes...";
            loading.style.display =
                "block";
        } else {
            analyzeButton.disabled = false;
            analyzeButton.textContent =
                "🔍 Analyze & Rank Candidates";
            loading.style.display =
                "none";
        }
    }
    function displayResults(data) {
        results.innerHTML = "";
        const vacancy =
            data.job_role ||
            jobRole.value.trim();
        const candidates =
            Array.isArray(data.candidates)
                ? data.candidates
                : [];
        const requiredSkills =
            Array.isArray(data.required_skills)
                ? data.required_skills
                : [];
        const header =
            document.createElement("div");
        header.className =
            "results-header";
        header.innerHTML = `
            <div>
                <h2>
                    🏆 AI Candidate Screening Results
                </h2>
                <p>
                    Vacancy:
                    <strong>
                        ${escapeHTML(vacancy)}
                    </strong>
                </p>
            </div>
            <div class="results-badge">
                ${candidates.length}
                Resume${candidates.length === 1 ? "" : "s"}
            </div>
        `;
        results.appendChild(header);
        const requiredSkillsCard =
            document.createElement("div");
        requiredSkillsCard.className =
            "required-skills-card";
        let requiredSkillsHTML = "";
        if (requiredSkills.length > 0) {
            requiredSkillsHTML =
                requiredSkills
                    .map(skill => `
                        <span class="
                            skill
                            required
                        ">
                            ✓
                            ${escapeHTML(skill)}
                        </span>
                    `)
                    .join("");
        } else {
            requiredSkillsHTML = `
                <div class="no-required-skills">
                    ⚠ No required skills were identified
                    for this vacancy.
                    <br><br>
                    Try entering a more specific job role,
                    such as:
                    <strong>
                        Java Backend Developer
                    </strong>
                </div>
            `;
        }
        requiredSkillsCard.innerHTML = `
            <div class="required-skills-header">
                <div>
                    <h3>
                        🎯 Required Skills for This Vacancy
                    </h3>
                    <p>
                        Skills identified from:
                        <strong>
                            ${escapeHTML(vacancy)}
                        </strong>
                    </p>
                </div>
                <div class="required-count">
                    ${requiredSkills.length}
                    Skills
                </div>
            </div>
            <div class="required-skills-list">
                ${requiredSkillsHTML}
            </div>
        `;
        results.appendChild(
            requiredSkillsCard
        );
        const summary =
            document.createElement("div");
        summary.className =
            "results-summary";
        summary.innerHTML = `
            <div class="summary-card">
                <span>
                    💼
                </span>
                <div>
                    <small>
                        Vacancy
                    </small>
                    <strong>
                        ${escapeHTML(vacancy)}
                    </strong>
                </div>
            </div>
            <div class="summary-card">
                <span>
                    📄
                </span>
                <div>
                    <small>
                        Resumes
                    </small>
                    <strong>
                        ${candidates.length}
                    </strong>
                </div>
            </div>
            <div class="summary-card">
                <span>
                    🎯
                </span>
                <div>
                    <small>
                        Required Skills
                    </small>
                    <strong>
                        ${requiredSkills.length}
                    </strong>
                </div>
            </div>
        `;
        results.appendChild(summary);
        candidates.forEach(
            (candidate, index) => {
                const card =
                    createCandidateCard(
                        candidate,
                        index,
                        vacancy
                    );
                results.appendChild(card);
            }
        );
        resultsSection.style.display =
            "block";
        setTimeout(() => {
            resultsSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }, 100);
    }
    function createCandidateCard(
        candidate,
        index,
        vacancy
    ) {
        const card =
            document.createElement("div");
        card.className =
            "candidate-card";
        const filename =
            candidate.filename ||
            `Candidate ${index + 1}`;
        const rank =
            Number(candidate.rank) ||
            index + 1;
        const eligibility =
            safeNumber(
                candidate.eligibility
            );
        const atsScore =
            safeNumber(
                candidate.ats_score
            );
        const skillScore =
            safeNumber(
                candidate.skill_score
            );
        const similarityScore =
            safeNumber(
                candidate.similarity_score
            );
        const experienceScore =
            safeNumber(
                candidate.experience_score
            );
        const roleScore =
            safeNumber(
                candidate.role_score
            );
        const educationScore =
            safeNumber(
                candidate.education_score
            );
        const projectScore =
            safeNumber(
                candidate.project_score
            );
        const certificationScore =
            safeNumber(
                candidate.certification_score
            );
        const stage =
            getEligibilityStage(
                eligibility
            );
        const matchedSkills =
            Array.isArray(
                candidate.matched_skills
            )
                ? candidate.matched_skills
                : [];
        const missingSkills =
            Array.isArray(
                candidate.missing_skills
            )
                ? candidate.missing_skills
                : [];
        const sections =
            candidate.sections || {};
        card.innerHTML = `
            <div class="candidate-top">
                <div class="candidate-info">
                    <div class="rank">
                        Rank #${rank}
                    </div>
                    <h3 class="candidate-name">
                        📄
                        ${escapeHTML(filename)}
                    </h3>
                    <div class="candidate-role">
                        Vacancy:
                        ${escapeHTML(vacancy)}
                    </div>
                </div>
                <div class="main-score">
                    <span>
                        ${eligibility}%
                    </span>
                    <small>
                        Eligibility
                    </small>
                </div>
            </div>
            <!-- FOUR STAGE STATUS -->
            <div class="
                eligibility-status
                ${stage.className}
            ">
                <div class="status-icon">
                    ${stage.icon}
                </div>
                <div class="status-content">
                    <strong>
                        ${stage.title}
                    </strong>
                    <span>
                        ${stage.description}
                    </span>
                </div>
            </div>
            <!-- STAGE SCALE -->
            <div class="eligibility-scale">
                ${stageBox(
                    1,
                    "Not Eligible",
                    stage.stage
                )}
                ${stageBox(
                    2,
                    "Eligible",
                    stage.stage
                )}
                ${stageBox(
                    3,
                    "Interview",
                    stage.stage
                )}
                ${stageBox(
                    4,
                    "Highly Recommended",
                    stage.stage
                )}
            </div>
            <!-- SCORE GRID -->
            <div class="score-grid">
                <div class="score-box">
                    <strong>
                        ${atsScore}
                    </strong>
                    <span>
                        ATS Score
                    </span>
                </div>
                <div class="score-box">
                    <strong>
                        ${skillScore}%
                    </strong>
                    <span>
                        Skills Match
                    </span>
                </div>
                <div class="score-box">
                    <strong>
                        ${similarityScore}%
                    </strong>
                    <span>
                        NLP Match
                    </span>
                </div>
                <div class="score-box">
                    <strong>
                        ${experienceScore}%
                    </strong>
                    <span>
                        Experience
                    </span>
                </div>
            </div>
            <!-- SCORE BREAKDOWN -->
            <div class="breakdown-section">
                <h4>
                    📊 Score Breakdown
                </h4>
                ${progressBar(
                    "Job Role",
                    roleScore
                )}
                ${progressBar(
                    "Education",
                    educationScore
                )}
                ${progressBar(
                    "Projects",
                    projectScore
                )}
                ${progressBar(
                    "Certifications",
                    certificationScore
                )}
            </div>
            <!-- MATCHED -->
            <div class="skills-section">
                <h4>
                    ✅ Matching / Available Skills
                </h4>
                <div class="skills">
                    ${
                        matchedSkills.length > 0
                        ?
                        matchedSkills
                            .map(skill => `
                                <span class="
                                    skill
                                    matched
                                ">
                                    ✓
                                    ${escapeHTML(skill)}
                                </span>
                            `)
                            .join("")
                        :
                        `<span class="skill">
                            No matching skills
                        </span>`
                    }
                </div>
            </div>
            <!-- MISSING -->
            <div class="skills-section">
                <h4>
                    ⚠ Required Skills Missing
                </h4>
                <div class="skills">
                    ${
                        missingSkills.length > 0
                        ?
                        missingSkills
                            .map(skill => `
                                <span class="
                                    skill
                                    missing
                                ">
                                    ⚠
                                    ${escapeHTML(skill)}
                                </span>
                            `)
                            .join("")
                        :
                        `
                            <span class="
                                skill
                                matched
                            ">
                                ✓
                                Candidate has all
                                identified required skills
                            </span>
                        `
                    }
                </div>
            </div>
            <!-- ATS SECTIONS -->
            <div class="sections-section">
                <h4>
                    📋 ATS Resume Sections
                </h4>
                <div class="sections">
                    ${sectionStatus(
                        "Education",
                        sections.education
                    )}
                    ${sectionStatus(
                        "Experience",
                        sections.experience
                    )}
                    ${sectionStatus(
                        "Projects",
                        sections.projects
                    )}
                    ${sectionStatus(
                        "Skills",
                        sections.skills
                    )}
                    ${sectionStatus(
                        "Certifications",
                        sections.certifications
                    )}
                </div>
            </div>
        `;
        return card;
    }
    function stageBox(
        number,
        title,
        currentStage
    ) {
        return `
            <div class="
                scale-step
                ${currentStage >= number ? "active" : ""}
            ">
                <span>
                    ${number}
                </span>
                ${title}
            </div>
        `;
    }
    function getEligibilityStage(score) {
        if (score < 40) {
            return {
                stage: 1,
                title: "NOT ELIGIBLE",
                description:
                    "Candidate does not meet the required vacancy criteria.",
                icon: "❌",
                className: "not-eligible"
            };
        }
        if (score < 60) {
            return {
                stage: 2,
                title: "ELIGIBLE",
                description:
                    "Candidate meets the basic requirements.",
                icon: "🟠",
                className: "eligible"
            };
        }
        if (score < 80) {
            return {
                stage: 3,
                title: "INTERVIEW RECOMMENDED",
                description:
                    "Candidate has a good match and should be considered for an interview.",
                icon: "🎯",
                className: "interview"
            };
        }
        return {
            stage: 4,
            title: "HIGHLY RECOMMENDED",
            description:
                "Candidate is a strong match for this vacancy.",
            icon: "✅",
            className: "highly-recommended"
        };
    }
    function progressBar(
        label,
        value
    ) {
        const score =
            Math.max(
                0,
                Math.min(
                    100,
                    safeNumber(value)
                )
            );
        return `
            <div class="breakdown-item">
                <div class="breakdown-header">
                    <span>
                        ${escapeHTML(label)}
                    </span>
                    <strong>
                        ${score}%
                    </strong>
                </div>
                <div class="progress">
                    <div
                        class="progress-bar"
                        style="width:${score}%"
                    ></div>
                </div>
            </div>
        `;
    }
    function sectionStatus(
        name,
        exists
    ) {
        return `
            <span class="
                section-status
                ${exists ? "found" : "missing"}
            ">
                ${exists ? "✓" : "✗"}
                ${escapeHTML(name)}
            </span>
        `;
    }
    function safeNumber(value) {
        const number =
            Number(value);
        if (!Number.isFinite(number)) {
            return 0;
        }
        return Math.round(
            number * 10
        ) / 10;
    }
    function formatFileSize(bytes) {
        if (!bytes || bytes <= 0) {
            return "0 Bytes";
        }
        const sizes = [
            "Bytes",
            "KB",
            "MB",
            "GB"
        ];
        const i =
            Math.floor(
                Math.log(bytes) /
                Math.log(1024)
            );
        return (
            Math.round(
                bytes /
                Math.pow(1024, i) *
                100
            ) / 100
        )
        + " "
        + sizes[i];
    }
    function escapeHTML(value) {
        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }
        const div =
            document.createElement("div");
        div.textContent =
            String(value);
        return div.innerHTML;
    }
    updateFileList();
});