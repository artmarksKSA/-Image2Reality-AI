import { useState } from 'react';

function App() {
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setMessage(`✅ تم اختيار ${selectedFiles.length} صورة`);
    setDownloadUrl(null);
  };

  const handleConvert = async () => {
    if (files.length === 0) {
      setMessage("⚠️ يرجى اختيار صور أولاً");
      return;
    }

    setLoading(true);
    setMessage("🔄 جاري رفع الصور ومعالجتها...");
    setDownloadUrl(null);

    try {
      // إنشاء FormData لإرسال الصور
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      // إرسال الصور للسيرفر
      const response = await fetch('https://image2reality-backend.onrender.comconvert', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('فشل الاتصال بالسيرفر');
      }

      const data = await response.json();
      
      setMessage(`✨ ${data.message}`);
      setDownloadUrl(data.download_url);
      
    } catch (error) {
      console.error(error);
      setMessage("❌ حدث خطأ: تأكد أن السيرفر يعمل على المنفذ 8000");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div dir="rtl" style={{
      minHeight: '100vh',
      background: `
        radial-gradient(circle at 20% 30%, rgba(60, 60, 60, 0.4) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(80, 80, 80, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(40, 40, 40, 0.5) 0%, transparent 70%),
        linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #0d0d0d 100%)
      `,
      color: 'white',
      fontFamily: 'Tahoma, Arial, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      
      {/* طبقة التموج الرمادي */}
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        background: `
          repeating-linear-gradient(45deg, transparent, transparent 100px, rgba(255, 255, 255, 0.02) 100px, rgba(255, 255, 255, 0.02) 200px),
          repeating-linear-gradient(-45deg, transparent, transparent 100px, rgba(255, 255, 255, 0.02) 100px, rgba(255, 255, 255, 0.02) 200px)
        `,
        pointerEvents: 'none'
      }} />

      <div style={{ position: 'relative', zIndex: 1, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        
        <h1 style={{ 
          fontSize: '3rem', 
          marginBottom: '25px',
          textAlign: 'center',
          color: '#ffffff',
          textShadow: '0 0 25px rgba(255, 255, 255, 0.4), 0 2px 10px rgba(0, 0, 0, 0.8)',
          lineHeight: '1.6',
          fontWeight: 'bold'
        }}>
          🎨 محول الصور إلى 3D
        </h1>
        
        <p style={{ 
          fontSize: '1.2rem', 
          marginBottom: '50px',
          textAlign: 'center',
          color: '#bbbbbb',
          lineHeight: '1.8',
          maxWidth: '600px'
        }}>
          ارفع صورك واحصل على موديل ثلاثي الأبعاد جاهز لبرنامج 3ds Max
        </p>

        <div style={{
          background: 'rgba(20, 20, 20, 0.7)',
          padding: '40px',
          borderRadius: '20px',
          backdropFilter: 'blur(15px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          maxWidth: '500px',
          width: '100%',
          textAlign: 'center',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)'
        }}>
          
          <label style={{
            display: 'block',
            padding: '25px',
            background: 'rgba(40, 40, 40, 0.5)',
            borderRadius: '12px',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginBottom: '20px',
            border: '2px dashed rgba(150, 150, 150, 0.4)',
            transition: 'all 0.3s ease',
            color: '#e0e0e0',
            opacity: loading ? 0.5 : 1
          }}>
            📁 اضغط هنا لاختيار الصور
            <input 
              type="file" 
              multiple 
              accept="image/*"
              onChange={handleFileChange}
              disabled={loading}
              style={{ display: 'none' }}
            />
          </label>

          {message && (
            <p style={{ 
              marginBottom: '20px',
              padding: '12px',
              background: 'rgba(0, 0, 0, 0.4)',
              borderRadius: '8px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#e0e0e0'
            }}>
              {message}
            </p>
          )}

          <button
            onClick={handleConvert}
            disabled={loading}
            style={{
              width: '100%',
              padding: '15px',
              fontSize: '1.2rem',
              background: loading 
                ? 'rgba(60, 60, 60, 0.5)' 
                : 'linear-gradient(135deg, #2a2a2a 0%, #4a4a4a 50%, #2a2a2a 100%)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '10px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.4)',
              marginBottom: downloadUrl ? '15px' : '0'
            }}>
            {loading ? '⏳ جاري المعالجة...' : '🚀 تحويل إلى 3D'}
          </button>

          {/* زر التحميل يظهر فقط بعد نجاح التحويل */}
          {downloadUrl && (
            <a
              href={downloadUrl}
              download
              style={{
                display: 'block',
                width: '100%',
                padding: '15px',
                fontSize: '1.1rem',
                background: 'linear-gradient(135deg, #1a4d2e 0%, #2d7a4a 50%, #1a4d2e 100%)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '10px',
                fontWeight: 'bold',
                border: '1px solid rgba(100, 255, 150, 0.3)',
                boxShadow: '0 4px 15px rgba(0, 100, 50, 0.3)'
              }}>
              ⬇️ تحميل الموديل (.obj)
            </a>
          )}
        </div>

        <footer style={{ 
          marginTop: '40px', 
          opacity: 0.5,
          color: '#aaaaaa'
        }}>
          صُنع بـ ❤️ | المشروع على GitHub قريباً
        </footer>
      </div>
    </div>
  );
}

export default App;