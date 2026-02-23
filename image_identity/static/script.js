// DOM 元素
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const clearBtn = document.getElementById('clear-btn');
const identifyBtn = document.getElementById('identify-btn');
const loading = document.getElementById('loading');
const resultSection = document.getElementById('result-section');
const errorMessage = document.getElementById('error-message');
const resultImage = document.getElementById('result-image');
const smilesOutput = document.getElementById('smiles-output');
const copyBtn = document.getElementById('copy-btn');

let uploadedFile = null;

// 点击上传区域
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// 文件选择
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

// 拖拽上传
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);
    }
});

// 处理文件
function handleFile(file) {
    uploadedFile = file;

    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
        dropZone.style.display = 'none';
        identifyBtn.disabled = false;

        // 隐藏之前的结果和错误
        resultSection.style.display = 'none';
        errorMessage.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// 清除按钮
clearBtn.addEventListener('click', () => {
    uploadedFile = null;
    fileInput.value = '';
    previewImage.src = '';
    previewContainer.style.display = 'none';
    dropZone.style.display = 'block';
    identifyBtn.disabled = true;
    resultSection.style.display = 'none';
    errorMessage.style.display = 'none';
});

// 识别按钮
identifyBtn.addEventListener('click', async () => {
    if (!uploadedFile) return;

    // 显示加载状态
    loading.style.display = 'block';
    identifyBtn.disabled = true;
    errorMessage.style.display = 'none';
    resultSection.style.display = 'none';

    // 创建 FormData
    const formData = new FormData();
    formData.append('image', uploadedFile);

    try {
        const response = await fetch('/identify', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // 显示结果
            smilesOutput.textContent = data.smiles;
            resultImage.src = data.image_url;
            resultSection.style.display = 'block';
        } else {
            showError(data.error || '识别失败，请重试');
        }
    } catch (error) {
        showError('网络错误，请检查服务器是否运行');
        console.error(error);
    } finally {
        loading.style.display = 'none';
        identifyBtn.disabled = false;
    }
});

// 复制 SMILES
copyBtn.addEventListener('click', async () => {
    const smiles = smilesOutput.textContent;
    try {
        await navigator.clipboard.writeText(smiles);

        // 显示复制成功提示
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
        `;
        copyBtn.style.color = 'var(--success-color)';
        copyBtn.style.borderColor = 'var(--success-color)';

        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.style.color = '';
            copyBtn.style.borderColor = '';
        }, 2000);
    } catch (error) {
        console.error('复制失败:', error);
    }
});

// 显示错误
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}
