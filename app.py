@app.route('/')
def index():
    """index.html をインラインで返す"""
    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>相談・助言記録票</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #1e40af;
            --primary-light: #3b82f6;
            --primary-dark: #1e3a8a;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-900: #111827;
            --text-light: #6b7280;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
            background: linear-gradient(135deg, var(--gray-50) 0%, #f0f4ff 100%);
            color: var(--gray-900);
            min-height: 100vh;
            padding: 1rem;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        .header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .header p {
            font-size: 0.95rem;
            opacity: 0.95;
        }

        .content {
            padding: 2rem;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }

        .section {
            margin-bottom: 2rem;
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary-light);
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--gray-700);
            font-size: 0.95rem;
        }

        input[type="text"],
        input[type="number"],
        input[type="date"],
        input[type="tel"],
        textarea,
        select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--gray-300);
            border-radius: 6px;
            font-family: inherit;
            font-size: 0.95rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        input[type="text"]:focus,
        input[type="number"]:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: var(--primary-light);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        textarea {
            resize: vertical;
            min-height: 80px;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
        }

        @media (max-width: 768px) {
            .grid-2, .grid-3 {
                grid-template-columns: 1fr;
            }
        }

        .audio-input-section {
            background: var(--gray-50);
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid var(--warning);
            margin-bottom: 1.5rem;
        }

        .file-upload-area {
            border: 2px dashed var(--warning);
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            background: white;
            margin-bottom: 1rem;
        }

        .file-upload-area:hover, 
        .file-upload-area.drag-over {
            border-color: var(--warning);
            background: rgba(245, 158, 11, 0.05);
        }

        .file-upload-area input[type="file"] {
            display: none;
        }

        .file-upload-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .file-upload-text {
            color: var(--gray-600);
            font-size: 0.9rem;
        }

        .file-name-display {
            font-size: 0.85rem;
            color: var(--primary);
            font-weight: 600;
            margin-top: 0.5rem;
        }

        button {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.95rem;
        }

        .btn-primary {
            background: var(--primary-light);
            color: white;
        }

        .btn-primary:hover:not(:disabled) {
            background: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
        }

        .btn-primary:disabled {
            background: #9ca3af;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .btn-warning {
            background: var(--warning);
            color: white;
        }

        .btn-warning:hover:not(:disabled) {
            background: #d97706;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }

        .btn-success {
            background: var(--success);
            color: white;
        }

        .btn-success:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        .btn-secondary {
            background: var(--gray-300);
            color: var(--gray-900);
        }

        .btn-secondary:hover {
            background: var(--gray-400);
        }

        .button-group {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }

        .alert {
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            display: none;
        }

        .alert.show {
            display: block;
        }

        #successAlert {
            background: #d1fae5;
            border-left: 4px solid var(--success);
            color: #065f46;
        }

        #errorAlert {
            background: #fee2e2;
            border-left: 4px solid var(--error);
            color: #7f1d1d;
        }

        .footer {
            background: var(--gray-100);
            color: var(--text-light);
            text-align: center;
            padding: 1.5rem;
            font-size: 0.85rem;
        }

        .processing {
            display: inline-block;
            width: 1rem;
            height: 1rem;
            border: 2px solid rgba(30, 64, 175, 0.3);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .transcription-section {
            background: #f0f9ff;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
            margin-bottom: 1.5rem;
        }

        .button-row {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 相談・助言記録票</h1>
            <p>高年齢者雇用確保措置に関する相談・助言の記録</p>
        </div>

        <div id="successAlert" class="alert"></div>
        <div id="errorAlert" class="alert"></div>

        <div class="content">
            <form id="reportForm">
                <!-- オーディオセクション -->
                <div class="audio-input-section">
                    <div class="section-title">🎵 Step 1: 音声ファイルをテキスト化</div>
                    
                    <div class="file-upload-area" id="uploadArea" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)" onclick="document.getElementById('audioFile').click()">
                        <div class="file-upload-icon">🎤</div>
                        <div class="file-upload-text">クリックまたはドラッグ＆ドロップで音声ファイルを選択</div>
                        <input type="file" id="audioFile" accept="audio/*" onchange="handleFileSelect(event)">
                        <div class="file-name-display" id="selectedFileName"></div>
                    </div>

                    <button type="button" class="btn-primary" id="transcribeBtn" onclick="transcribeAudio()" disabled>
                        🎤 テキスト化（自動処理）
                    </button>
                </div>

                <!-- フォーム本体 -->
                <div class="section">
                    <div class="section-title">1. 企業の属性</div>
                    
                    <div class="grid-3">
                        <div class="form-group">
                            <label for="visitYear">相談・助言実施日</label>
                            <div class="grid-3">
                                <input type="number" id="visitYear" name="visitYear" min="2020" max="2100" placeholder="年">
                                <input type="number" id="visitMonth" name="visitMonth" min="1" max="12" placeholder="月">
                                <input type="number" id="visitDay" name="visitDay" min="1" max="31" placeholder="日">
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="reportYear">支部報告日</label>
                            <div class="grid-3">
                                <input type="number" id="reportYear" name="reportYear" min="2020" max="2100" placeholder="年">
                                <input type="number" id="reportMonth" name="reportMonth" min="1" max="12" placeholder="月">
                                <input type="number" id="reportDay" name="reportDay" min="1" max="31" placeholder="日">
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="officeNumber">①適用事業所番号</label>
                        <input type="text" id="officeNumber" name="officeNumber" placeholder="">
                    </div>

                    <div class="form-group">
                        <label for="companyName">③名称</label>
                        <input type="text" id="companyName" name="companyName" placeholder="">
                    </div>

                    <div class="form-group">
                        <label for="address">④所在地</label>
                        <input type="text" id="address" name="address" placeholder="">
                    </div>

                    <div class="form-group">
                        <label for="visitAddress">⑤訪問先住所</label>
                        <input type="text" id="visitAddress" name="visitAddress" placeholder="">
                    </div>

                    <div class="form-group">
                        <label for="phone">⑥電話番号</label>
                        <input type="tel" id="phone" name="phone" placeholder="">
                    </div>

                    <div class="form-group">
                        <label for="contactPerson">⑦面接者の役職氏名</label>
                        <input type="text" id="contactPerson" name="contactPerson" placeholder="">
                    </div>

                    <div class="form-group">
                        <label for="companyOverview">会社概要</label>
                        <textarea id="companyOverview" name="companyOverview" placeholder="企業の概要を記入"></textarea>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">2. 訪問のきっかけ</div>

                    <div class="form-group">
                        <label for="motivation">訪問のきっかけ</label>
                        <select id="motivation" name="motivation">
                            <option value="">選択してください</option>
                            <option value="1">管轄ハローワークからの依頼</option>
                            <option value="2">企業からの相談申し込み</option>
                            <option value="3">既往相談企業からの再相談</option>
                            <option value="4">その他</option>
                        </select>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">3. 相談・助言実施方法</div>

                    <div class="form-group">
                        <label for="method">相談・助言実施方法</label>
                        <select id="method" name="method">
                            <option value="">選択してください</option>
                            <option value="1">来所相談</option>
                            <option value="2">訪問相談</option>
                            <option value="3">電話相談</option>
                            <option value="4">オンライン相談</option>
                        </select>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">4. 会社概要（労働構造等）</div>

                    <div class="form-group">
                        <label for="laborStructure">①労働構造</label>
                        <select id="laborStructure" name="laborStructure">
                            <option value="">選択してください</option>
                            <option value="1">～20代</option>
                            <option value="2">30代</option>
                            <option value="3">40代</option>
                            <option value="4">50代</option>
                            <option value="5">60代</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="laborStructureDetail">具体的な状況</label>
                        <textarea id="laborStructureDetail" name="laborStructureDetail" placeholder="年代別人数など"></textarea>
                    </div>

                    <div class="form-group">
                        <label for="recruitment">②採用状況</label>
                        <select id="recruitment" name="recruitment">
                            <option value="">選択してください</option>
                            <option value="1">採用できている</option>
                            <option value="2">あまり採用できていない</option>
                            <option value="3">採用できていない</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="recruitmentDetail">具体的な状況</label>
                        <textarea id="recruitmentDetail" name="recruitmentDetail" placeholder="採用方法、課題など"></textarea>
                    </div>

                    <div class="form-group">
                        <label for="seniorEmployment">③高齢者の活用</label>
                        <select id="seniorEmployment" name="seniorEmployment">
                            <option value="">選択してください</option>
                            <option value="1">活用できている</option>
                            <option value="2">あまり活用できていない</option>
                            <option value="3">活用できていない</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="seniorEmploymentDetail">具体的な状況（業務内容等）</label>
                        <textarea id="seniorEmploymentDetail" name="seniorEmploymentDetail" placeholder="人数、職務内容など"></textarea>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">5. 高年齢者雇用の改善・課題</div>

                    <div class="form-group">
                        <label for="employmentMeasures">雇用確保措置</label>
                        <select id="employmentMeasures" name="employmentMeasures">
                            <option value="">選択してください</option>
                            <option value="1">未実施企業</option>
                            <option value="2">実施中企業</option>
                            <option value="3">実施済み企業</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="issues">課題</label>
                        <textarea id="issues" name="issues" placeholder="特定された課題を記入"></textarea>
                    </div>

                    <div class="form-group">
                        <label for="advice">助言内容</label>
                        <textarea id="advice" name="advice" placeholder="提供した助言内容"></textarea>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">6. 相談・助言の成果</div>

                    <div class="form-group">
                        <label for="conclusion">結論</label>
                        <select id="conclusion" name="conclusion">
                            <option value="">選択してください</option>
                            <option value="1">できるだけ早い機会に再訪問が必要</option>
                            <option value="2">具体的な支援が可能</option>
                            <option value="3">更なる改善が期待できる</option>
                            <option value="4">先駆的に取り組んでいる</option>
                            <option value="5">当面さらなる改善は期待できない</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="conclusionReason">所見理由</label>
                        <textarea id="conclusionReason" name="conclusionReason" placeholder=""></textarea>
                    </div>
                </div>

                <!-- ボタングループ -->
                <div class="button-group">
                    <button type="button" class="btn-success" onclick="downloadAsExcel()">
                        📊 Excelで出力
                    </button>
                    <button type="reset" class="btn-secondary">
                        🔄 リセット
                    </button>
                </div>
            </form>
        </div>

        <div class="footer">
            <p>© 2026 相談・助言記録票 | Railway Speech API 連携版</p>
        </div>
    </div>

    <script>
        let selectedAudioFile = null;
        const RAILWAY_API_URL = 'https://web-production-705d8d.up.railway.app/transcribe';

        function handleDragOver(e) {
            e.preventDefault();
            document.getElementById('uploadArea').classList.add('drag-over');
        }

        function handleDragLeave(e) {
            document.getElementById('uploadArea').classList.remove('drag-over');
        }

        function handleDrop(e) {
            e.preventDefault();
            document.getElementById('uploadArea').classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file) setAudioFile(file);
        }

        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (file) setAudioFile(file);
        }

        function setAudioFile(file) {
            selectedAudioFile = file;
            document.getElementById('selectedFileName').textContent = `📎 ${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)`;
            document.getElementById('transcribeBtn').disabled = false;
            showAlert('✅ ファイルを選択しました。「🎤 テキスト化」ボタンをクリックしてください。', 'success');
        }

        async function transcribeAudio() {
            if (!selectedAudioFile) {
                showAlert('❌ ファイルを選択してください', 'error');
                return;
            }

            const btn = document.getElementById('transcribeBtn');
            btn.disabled = true;
            const originalText = btn.textContent;
            btn.textContent = '🔄 処理中...';

            try {
                const formData = new FormData();
                formData.append('file', selectedAudioFile);

                const response = await fetch(RAILWAY_API_URL, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`API Error: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    document.getElementById('issues').value = data.transcript;
                    showAlert('✅ テキスト化が完了しました！「課題」欄に自動入力されています。必要に応じて編集してください。', 'success');
                } else {
                    showAlert(`❌ テキスト化に失敗しました: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert(`❌ エラーが発生しました: ${error.message}`, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        }

        function showAlert(message, type) {
            const alertId = type === 'success' ? 'successAlert' : 'errorAlert';
            const alert = document.getElementById(alertId);
            alert.textContent = message;
            alert.classList.add('show');
            setTimeout(() => alert.classList.remove('show'), 5000);
        }

        function downloadAsExcel() {
            const formData = new FormData(document.getElementById('reportForm'));
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            const wb = XLSX.utils.book_new();
            const ws_data = [
                ['相談・助言記録票'],
                [''],
                ['1. 企業の属性'],
                ['相談・助言実施日', `${data.visitYear}年${data.visitMonth}月${data.visitDay}日`],
                ['支部報告日', `${data.reportYear}年${data.reportMonth}月${data.reportDay}日`],
                ['①適用事業所番号', data.officeNumber || ''],
                ['③名称', data.companyName || ''],
                ['④所在地', data.address || ''],
                ['⑤訪問先住所', data.visitAddress || ''],
                ['⑥電話番号', data.phone || ''],
                ['⑦面接者の役職氏名', data.contactPerson || ''],
                ['会社概要', data.companyOverview || ''],
                [''],
                ['2. 訪問のきっかけ'],
                ['訪問のきっかけ', data.motivation || ''],
                [''],
                ['3. 実施方法'],
                ['相談・助言実施方法', data.method || ''],
                [''],
                ['4. 会社概要（労働構造等）'],
                ['①労働構造', data.laborStructure || ''],
                ['具体的な状況', data.laborStructureDetail || ''],
                ['②採用状況', data.recruitment || ''],
                ['具体的な状況', data.recruitmentDetail || ''],
                ['③高齢者の活用', data.seniorEmployment || ''],
                ['具体的な状況', data.seniorEmploymentDetail || ''],
                [''],
                ['5. 高年齢者雇用の改善・課題'],
                ['雇用確保措置', data.employmentMeasures || ''],
                ['課題', data.issues || ''],
                ['助言内容', data.advice || ''],
                [''],
                ['6. 相談・助言の成果'],
                ['結論', data.conclusion || ''],
                ['所見理由', data.conclusionReason || '']
            ];

            const ws = XLSX.utils.aoa_to_sheet(ws_data);
            XLSX.utils.book_append_sheet(wb, ws, '相談助言記録票');
            XLSX.writeFile(wb, `相談助言記録票_${new Date().getTime()}.xlsx`);
            showAlert('✅ Excelファイルをダウンロードしました', 'success');
        }

        window.addEventListener('load', () => {
            const today = new Date();
            document.getElementById('visitYear').value = today.getFullYear();
            document.getElementById('visitMonth').value = today.getMonth() + 1;
            document.getElementById('visitDay').value = today.getDate();
            document.getElementById('reportYear').value = today.getFullYear();
            document.getElementById('reportMonth').value = today.getMonth() + 1;
            document.getElementById('reportDay').value = today.getDate();
        });
    </script>
</body>
</html>"""
    return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
