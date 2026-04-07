import { Component, onMounted, useState, xml } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

// ---------------------------------------------------------------------------
// Minimal CSS — uses Odoo's existing Bootstrap / backend variables so the
// translator blends seamlessly with the rest of the ERP's light theme.
// ---------------------------------------------------------------------------
const INJECT_CSS = `
.o_translator_page {
    padding: 24px;
    max-width: 1100px;
    margin: 0 auto;
}
.o_translator_lang_row {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}
.o_translator_lang_row .o_field_widget {
    flex: 1;
    min-width: 160px;
}
.o_translator_text_grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
@media (max-width: 768px) {
    .o_translator_text_grid { grid-template-columns: 1fr; }
    .o_translator_lang_row { gap: 8px; }
}
.o_translator_textarea_wrap {
    display: flex;
    flex-direction: column;
    gap: 6px;
    position: relative; /* Allow positioning buttons inside */
}
.o_translator_textarea_label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--o-label-color, #6c757d);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.o_translator_textarea {
    width: 100%;
    border: 1px solid var(--bs-border-color, #dee2e6);
    border-radius: 6px;
    padding: 10px 12px;
    padding-bottom: 40px; /* Space for buttons */
    font-size: 0.95rem;
    font-family: inherit;
    resize: vertical;
    min-height: 180px;
    line-height: 1.6;
    background: #fff;
    color: #212529;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.o_translator_textarea:focus {
    outline: none;
    border-color: var(--o-form-valid-color, #017e84);
    box-shadow: 0 0 0 2px rgba(1,126,132,0.15);
}
.o_translator_textarea[readonly] {
    background: #f8f9fa;
    color: #495057;
}
.o_translator_char_count {
    font-size: 0.72rem;
    color: #adb5bd;
    text-align: right;
}
.o_translator_inner_controls {
    position: absolute;
    bottom: 30px;
    right: 12px;
    display: flex;
    gap: 8px;
    background: rgba(255,255,255,0.8);
    padding: 4px;
    border-radius: 4px;
    z-index: 10;
}
.o_translator_icon_btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #dee2e6;
    background: #fff;
    border-radius: 50%;
    color: #6c757d;
    cursor: pointer;
    transition: all 0.15s;
}
.o_translator_icon_btn:hover:not(:disabled) {
    background: #f8f9fa;
    color: var(--o-form-valid-color, #017e84);
    border-color: var(--o-form-valid-color, #017e84);
}
.o_translator_icon_btn:disabled {
    opacity: 0.5;
    cursor: default;
}
.o_translator_icon_btn.active {
    background: #e8f5e9;
    color: #2e7d32;
    border-color: #2e7d32;
    animation: speaker-pulse 1s infinite;
}
@keyframes speaker-pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}
.o_translator_result_controls {
    display: flex;
    gap: 6px;
    justify-content: flex-end;
    align-items: center;
}
.o_translator_mic_btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid #dee2e6;
    background: #fff;
    color: #495057;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.15s;
    line-height: 1;
}
.o_translator_mic_btn:hover { background: #f0f0f0; }
.o_translator_mic_btn.is-recording {
    background: #fff0f0;
    border-color: #dc3545;
    color: #dc3545;
    animation: mic-pulse 1.2s ease-in-out infinite;
}
@keyframes mic-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220,53,69,0.3); }
    50% { box-shadow: 0 0 0 5px rgba(220,53,69,0); }
}
.o_translator_error {
    margin-top: 12px;
    padding: 8px 12px;
    background: #fff3f3;
    border: 1px solid #f5c6cb;
    border-radius: 6px;
    color: #721c24;
    font-size: 0.85rem;
}
.o_translator_footer {
    margin-top: 20px;
    padding-top: 12px;
    border-top: 1px solid #dee2e6;
    font-size: 0.78rem;
    color: #adb5bd;
}
.o_translator_footer a { color: #0d6efd; text-decoration: none; }
.o_translator_footer a:hover { text-decoration: underline; }
.o_translator_spinner {
    display: inline-block;
    width: 0.85em;
    height: 0.85em;
    border: 2px solid rgba(255,255,255,0.4);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
    vertical-align: middle;
    margin-right: 4px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.o_translator_select {
    border: 1px solid var(--bs-border-color, #dee2e6);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 0.95rem;
    background: #fff;
    color: #212529;
    cursor: pointer;
    transition: border-color 0.15s;
    min-width: 160px;
}
.o_translator_select:focus {
    outline: none;
    border-color: var(--o-form-valid-color, #017e84);
    box-shadow: 0 0 0 2px rgba(1,126,132,0.15);
}
.o_translator_swap_btn {
    background: none;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    color: #6c757d;
    padding: 6px 10px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.15s;
    white-space: nowrap;
    align-self: flex-end;
}
.o_translator_swap_btn:hover {
    background: #f0f0f0;
    color: #212529;
}
.o_translator_mic_unsupported {
    font-size: 0.75rem;
    color: #adb5bd;
    font-style: italic;
}
`;

function injectStyles() {
    if (document.getElementById("o_translator_css_v2")) return;
    const el = document.createElement("style");
    el.id = "o_translator_css_v2";
    el.textContent = INJECT_CSS;
    document.head.appendChild(el);
}

// ---------------------------------------------------------------------------
// Client-side fallback language list.
// Used when the Odoo proxy route is not yet available (module not restarted)
// or all LibreTranslate instances are unreachable.
// ---------------------------------------------------------------------------
const FALLBACK_LANGUAGES = [
    { code: "ar", name: "Arabic" },
    { code: "zh", name: "Chinese" },
    { code: "cs", name: "Czech" },
    { code: "nl", name: "Dutch" },
    { code: "en", name: "English" },
    { code: "fr", name: "French" },
    { code: "de", name: "German" },
    { code: "el", name: "Greek" },
    { code: "hi", name: "Hindi" },
    { code: "hu", name: "Hungarian" },
    { code: "id", name: "Indonesian" },
    { code: "it", name: "Italian" },
    { code: "ja", name: "Japanese" },
    { code: "ko", name: "Korean" },
    { code: "fa", name: "Persian" },
    { code: "pl", name: "Polish" },
    { code: "pt", name: "Portuguese" },
    { code: "ro", name: "Romanian" },
    { code: "ru", name: "Russian" },
    { code: "es", name: "Spanish" },
    { code: "sv", name: "Swedish" },
    { code: "tr", name: "Turkish" },
    { code: "uk", name: "Ukrainian" },
    { code: "ur", name: "Urdu" },
    { code: "vi", name: "Vietnamese" },
];

// ---------------------------------------------------------------------------
// SpeechRecognition helper
// ---------------------------------------------------------------------------
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;

/**
 * TranslatorDashboard — OWL client-action component.
 *
 * Provides an in-app translation UI via the Odoo server-side LibreTranslate
 * proxy (avoids CORS). Includes Web Speech API microphone input where
 * supported (Chrome, Edge). Design matches Odoo's standard backend light theme.
 */
export class TranslatorDashboard extends Component {
    static props = { ...standardActionServiceProps };

    static template = xml`
<div class="o_translator_page">

    <!-- Page title — same style as Odoo's "Settings" pages -->
    <div class="o_setting_header mb-4">
        <h2 class="mt-0" style="font-size:1.4rem; font-weight:600; color:#333;">
            <i class="fa fa-language me-2" style="color:var(--o-form-valid-color, #017e84);"/>
            Translator
        </h2>
        <p class="text-muted mb-0" style="font-size:0.875rem;">
            Free machine translation via LibreTranslate. Text is routed through this server — results may vary.
        </p>
    </div>

    <!-- Language selector row -->
    <div class="o_translator_lang_row">

        <div>
            <div class="o_translator_textarea_label mb-1">From</div>
            <select class="o_translator_select"
                    id="translator_source_lang"
                    t-model="state.sourceLang">
                <option value="auto">Auto-detect</option>
                <t t-foreach="state.languages" t-as="lang" t-key="lang.code">
                    <option t-att-value="lang.code" t-esc="lang.name"/>
                </t>
            </select>
        </div>

        <button class="o_translator_swap_btn"
                title="Swap languages"
                id="translator_swap_btn"
                t-on-click="onSwap">
            &#8644; Swap
        </button>

        <div>
            <div class="o_translator_textarea_label mb-1">To</div>
            <select class="o_translator_select"
                    id="translator_target_lang"
                    t-model="state.targetLang">
                <t t-foreach="state.languages" t-as="lang" t-key="lang.code">
                    <option t-att-value="lang.code" t-esc="lang.name"/>
                </t>
            </select>
        </div>

        <!-- Translate button pushed to the right -->
        <div class="ms-auto">
            <div class="o_translator_textarea_label mb-1" style="visibility:hidden;">.</div>
            <button class="btn btn-primary"
                    id="translator_translate_btn"
                    t-on-click="onTranslate"
                    t-att-disabled="state.isLoading || !state.sourceText.trim()">
                <t t-if="state.isLoading">
                    <span class="o_translator_spinner"/>Translating…
                </t>
                <t t-else="">
                    <i class="fa fa-exchange me-1"/> Translate
                </t>
            </button>
        </div>
    </div>

    <!-- Text panels -->
    <div class="o_translator_text_grid">

        <!-- Source panel -->
        <div class="o_translator_textarea_wrap">
            <div class="d-flex align-items-center justify-content-between mb-1">
                <span class="o_translator_textarea_label">Source text</span>
                <!-- Mic button -->
                <t t-if="state.speechSupported">
                    <button class="o_translator_mic_btn"
                            id="translator_mic_btn"
                            t-att-class="state.isRecording ? 'o_translator_mic_btn is-recording' : 'o_translator_mic_btn'"
                            t-on-click="onMicToggle"
                            t-att-title="state.isRecording ? 'Click to stop' : 'Click to speak'">
                        <i t-att-class="state.isRecording ? 'fa fa-microphone' : 'fa fa-microphone-slash'"/>
                        <t t-esc="state.isRecording ? ' Stop' : ' Speak'"/>
                    </button>
                </t>
                <t t-else="">
                    <span class="o_translator_mic_unsupported">
                        <i class="fa fa-microphone-slash me-1"/>Mic not available
                    </span>
                </t>
            </div>
            <textarea class="o_translator_textarea"
                      id="translator_source_text"
                      placeholder="Type, paste, or speak text to translate…"
                      t-model="state.sourceText"
                      t-on-input="onSourceInput"
                      rows="9"/>
            <div class="o_translator_char_count"
                 t-esc="state.sourceText.length + ' characters'"/>
        </div>

        <!-- Result panel -->
        <div class="o_translator_textarea_wrap">
            <div class="d-flex align-items-center justify-content-between mb-1">
                <span class="o_translator_textarea_label">Translation</span>
                <div class="o_translator_result_controls">
                    <button class="o_translator_mic_btn"
                            id="translator_clear_btn"
                            t-on-click="onClear"
                            title="Clear all">
                        <i class="fa fa-trash-o"/> Clear
                    </button>
                </div>
            </div>
            
            <textarea class="o_translator_textarea"
                      id="translator_result_text"
                      readonly="readonly"
                      rows="9"
                      t-att-placeholder="state.isLoading ? 'Translating…' : 'Translation will appear here'"
                      t-att-value="state.result"/>

            <!-- Floating Speaker and Copy icons inside the box -->
            <div class="o_translator_inner_controls" t-if="state.result">
                <button class="o_translator_icon_btn"
                        t-att-class="{active: state.isPlaying}"
                        t-on-click="onListen"
                        title="Listen to translation">
                    <i t-att-class="state.isPlaying ? 'fa fa-volume-up' : 'fa fa-bullhorn'"/>
                </button>
                <button class="o_translator_icon_btn"
                        t-on-click="onCopy"
                        title="Copy to clipboard">
                    <i class="fa fa-copy"/>
                </button>
            </div>

            <div class="o_translator_char_count"
                 t-esc="state.result.length + ' characters'"/>
        </div>
    </div>

    <!-- Restart needed banner -->
    <div t-if="!state.routesReady" style="margin-top:12px; padding:10px 14px; background:#fff8e1; border:1px solid #ffe082; border-radius:6px; font-size:0.85rem; color:#5d4037;">
        <i class="fa fa-info-circle me-1" style="color:#f59e0b;"/>
        <strong>Odoo restart required</strong> — The translation proxy routes are not loaded yet.
        Language selection uses a built-in list. To enable live translation, restart Odoo with:
        <code style="background:#f5f5f5; padding:1px 5px; border-radius:3px; font-size:0.8rem;">python odoo-bin -u refugee_crisis_erp -c odoo.conf</code>
    </div>

    <!-- Error -->
    <div t-if="state.error" class="o_translator_error">
        <i class="fa fa-exclamation-triangle me-1"/>
        <t t-esc="state.error"/>
    </div>

    <!-- Footer attribution -->
    <div class="o_translator_footer">
        Powered by <a href="https://libretranslate.de" target="_blank" rel="noopener">LibreTranslate</a>
        (free, open-source machine translation ·
        <a href="https://github.com/LibreTranslate/LibreTranslate" target="_blank" rel="noopener">GitHub</a>).
        Voice input uses your browser's built-in speech recognition (Chrome/Edge).
    </div>

</div>
    `;

    setup() {
        injectStyles();

        this.state = useState({
            languages: [],
            sourceLang: "auto",
            targetLang: "en",
            sourceText: "",
            result: "",
            isLoading: false,
            isRecording: false,
            isPlaying: false,
            speechSupported: !!SpeechRecognition,
            ttsSupported: !!window.speechSynthesis,
            error: "",
            routesReady: true,   // set to false when proxy routes aren't loaded yet
        });

        this._recognition = null;

        onMounted(() => this._loadLanguages());
    }

    // ------------------------------------------------------------------
    // Language loading
    // ------------------------------------------------------------------

    async _loadLanguages() {
        try {
            const langs = await rpc("/refugee_crisis_erp/translate/languages");
            if (langs && langs.error) throw new Error(langs.error);
            if (langs && Array.isArray(langs)) {
                langs.sort((a, b) => a.name.localeCompare(b.name));
                this.state.languages = langs;
                this.state.routesReady = true;
            } else {
                throw new Error("Invalid response");
            }
        } catch (err) {
            // If RPC fails with 404 or similar, it might be the route not being ready
            this.state.routesReady = false;
            this.state.languages = [...FALLBACK_LANGUAGES];
            console.warn("[Translator] Language list fetch failed, using fallback:", err.message);
        }
        if (!this.state.languages.some((l) => l.code === this.state.targetLang)) {
            this.state.targetLang = this.state.languages[0]?.code || "en";
        }
    }

    // ------------------------------------------------------------------
    // Translate
    // ------------------------------------------------------------------

    async onTranslate() {
        const text = this.state.sourceText.trim();
        if (!text) return;
        this.state.isLoading = true;
        this.state.error = "";
        this.state.result = "";
        try {
            const data = await rpc("/refugee_crisis_erp/translate", {
                q: text,
                source: this.state.sourceLang,
                target: this.state.targetLang,
            });
            this.state.routesReady = true;
            if (data && data.error) {
                this.state.error = data.error;
            } else if (data && data.translatedText) {
                this.state.result = data.translatedText;
            } else {
                this.state.error = "Unknown error from translation service.";
            }
        } catch (err) {
            // Check if it's a 404/route error
            if (err && err.message && (err.message.includes("404") || err.message.includes("not found"))) {
                this.state.routesReady = false;
            } else {
                this.state.error = `Translation error: ${err.message || "Unknown error"}`;
            }
        } finally {
            this.state.isLoading = false;
        }
    }

    // ------------------------------------------------------------------
    // Swap
    // ------------------------------------------------------------------

    onSwap() {
        if (this.state.sourceLang !== "auto") {
            [this.state.sourceLang, this.state.targetLang] =
                [this.state.targetLang, this.state.sourceLang];
        }
        if (this.state.result) {
            this.state.sourceText = this.state.result;
            this.state.result = "";
        }
    }

    // ------------------------------------------------------------------
    // Copy, clear, input, listen
    // ------------------------------------------------------------------
    
    onListen() {
        if (!window.speechSynthesis || !this.state.result) return;
        
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(this.state.result);
        utterance.lang = this._toBcp47(this.state.targetLang);
        
        utterance.onstart = () => { this.state.isPlaying = true; };
        utterance.onend = () => { this.state.isPlaying = false; };
        utterance.onerror = () => { this.state.isPlaying = false; };
        
        window.speechSynthesis.speak(utterance);
    }

    async onCopy() {
        if (!this.state.result) return;
        try {
            await navigator.clipboard.writeText(this.state.result);
        } catch {
            const el = document.getElementById("translator_result_text");
            if (el) { el.select(); document.execCommand("copy"); }
        }
    }

    onClear() {
        this.state.sourceText = "";
        this.state.result = "";
        this.state.error = "";
    }

    onSourceInput() {
        this.state.result = "";
        this.state.error = "";
    }

    // ------------------------------------------------------------------
    // Microphone / Web Speech API
    // ------------------------------------------------------------------

    onMicToggle() {
        if (!SpeechRecognition) return;
        if (this.state.isRecording) {
            this._stopRecording();
        } else {
            this._startRecording();
        }
    }

    _startRecording() {
        this.state.error = "";
        const rec = new SpeechRecognition();

        // Map source-lang code to BCP-47 where needed
        const langCode = this.state.sourceLang !== "auto"
            ? this._toBcp47(this.state.sourceLang)
            : undefined;
        if (langCode) rec.lang = langCode;

        rec.continuous = true;        // keep recording until user clicks Stop
        rec.interimResults = true;    // show partial results while speaking
        rec.maxAlternatives = 1;

        let finalTranscript = this.state.sourceText;

        rec.onresult = (event) => {
            let interim = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += (finalTranscript ? " " : "") + transcript.trim();
                } else {
                    interim = transcript;
                }
            }
            this.state.sourceText = finalTranscript + (interim ? " " + interim : "");
        };

        rec.onerror = (event) => {
            if (event.error === "not-allowed") {
                this.state.error = "Microphone permission denied. Please allow microphone access in your browser.";
            } else if (event.error !== "no-speech") {
                this.state.error = `Speech recognition error: ${event.error}`;
            }
            this.state.isRecording = false;
        };

        rec.onend = () => {
            // Restart if still marked as recording (continuous mode can auto-stop)
            if (this.state.isRecording) {
                try { rec.start(); } catch { this.state.isRecording = false; }
            }
        };

        try {
            rec.start();
            this._recognition = rec;
            this.state.isRecording = true;
        } catch (err) {
            this.state.error = `Could not start microphone: ${err.message}`;
        }
    }

    _stopRecording() {
        if (this._recognition) {
            this._recognition.onend = null; // prevent auto-restart
            this._recognition.stop();
            this._recognition = null;
        }
        this.state.isRecording = false;
    }

    /**
     * Convert LibreTranslate 2-letter codes to BCP-47 tags for SpeechRecognition.
     * Most are identical; a few need a region suffix.
     */
    _toBcp47(code) {
        const map = {
            ar: "ar-SA", zh: "zh-CN", en: "en-US", fr: "fr-FR", de: "de-DE",
            es: "es-ES", pt: "pt-PT", ru: "ru-RU", ja: "ja-JP", ko: "ko-KR",
            it: "it-IT", nl: "nl-NL", pl: "pl-PL", tr: "tr-TR", uk: "uk-UA",
            hi: "hi-IN", fa: "fa-IR", ur: "ur-PK", vi: "vi-VN", id: "id-ID",
        };
        return map[code] || code;
    }
}

registry.category("actions").add("refugee_crisis_erp.translator_dashboard", TranslatorDashboard);
