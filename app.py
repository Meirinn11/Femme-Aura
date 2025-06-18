from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Database rekomendasi obat lebih lengkap
DRUG_RECOMMENDATIONS = {
    "kram": {
        "20000": [
            {"nama": "Paracetamol 500mg", "harga": "Rp15.000", "deskripsi": "Untuk nyeri ringan sampai sedang"},
            {"nama": "Bodrex", "harga": "Rp10.000", "deskripsi": "Mengatasi nyeri haid ringan"}
        ],
        "50000": [
            {"nama": "Ponstan 250mg", "harga": "Rp35.000", "deskripsi": "Untuk kram menstruasi sedang"},
            {"nama": "Mefinal 250mg", "harga": "Rp40.000", "deskripsi": "Anti nyeri dan anti inflamasi"}
        ],
        "100000": [
            {"nama": "Celebrex 200mg", "harga": "Rp85.000", "deskripsi": "Untuk nyeri haid berat"},
            {"nama": "Arcoxia 60mg", "harga": "Rp95.000", "deskripsi": "Mengatasi nyeri dan inflamasi"}
        ]
    },
    "pusing": {
        "20000": [
            {"nama": "Paracetamol 500mg", "harga": "Rp15.000", "deskripsi": "Meredakan pusing ringan"},
            {"nama": "Bodrex", "harga": "Rp10.000", "deskripsi": "Untuk sakit kepala tegang"}
        ],
        "50000": [
            {"nama": "Panadol Extra", "harga": "Rp30.000", "deskripsi": "Mengandung kafein untuk pusing sedang"},
            {"nama": "Decolgen", "harga": "Rp25.000", "deskripsi": "Untuk pusing disertai flu"}
        ],
        "100000": [
            {"nama": "Sumagesic", "harga": "Rp75.000", "deskripsi": "Untuk migrain berat"},
            {"nama": "Migran", "harga": "Rp80.000", "deskripsi": "Khusus sakit kepala sebelah"}
        ]
    },
    "mual": {
        "20000": [
            {"nama": "Antimo", "harga": "Rp12.000", "deskripsi": "Untuk mual dan mabuk perjalanan"},
            {"nama": "Promag", "harga": "Rp8.000", "deskripsi": "Mengatasi mual karena maag"}
        ],
        "50000": [
            {"nama": "Vometa", "harga": "Rp35.000", "deskripsi": "Untuk mual dan muntah"},
            {"nama": "Stemetil", "harga": "Rp45.000", "deskripsi": "Mengatasi mual berat"}
        ],
        "100000": [
            {"nama": "Motilium", "harga": "Rp90.000", "deskripsi": "Untuk gangguan pencernaan"},
            {"nama": "Domperidone", "harga": "Rp85.000", "deskripsi": "Mengatasi mual kronis"}
        ]
    },
    "lelah": {
        "20000": [
            {"nama": "Hemaviton", "harga": "Rp5.000", "deskripsi": "Suplemen energi"},
            {"nama": "Enervon-C", "harga": "Rp15.000", "deskripsi": "Vitamin C dan B kompleks"}
        ],
        "50000": [
            {"nama": "Fatigon", "harga": "Rp35.000", "deskripsi": "Mengatasi lelah fisik"},
            {"nama": "Neurobion", "harga": "Rp40.000", "deskripsi": "Vitamin neurotropik"}
        ],
        "100000": [
            {"nama": "Blackmores", "harga": "Rp95.000", "deskripsi": "Multivitamin lengkap"},
            {"nama": "Youvit", "harga": "Rp85.000", "deskripsi": "Multivitamin wanita"}
        ]
    }
}

# Tips berdasarkan fase siklus menstruasi
CYCLE_TIPS = {
    "menstruasi": [
        "Gunakan pembalut yang nyaman",
        "Perbanyak konsumsi zat besi",
        "Hindari aktivitas berat"
    ],
    "folikular": [
        "Waktu terbaik untuk olahraga",
        "Tingkatkan asupan protein",
        "Mulai persiapan ovulasi"
    ],
    "ovulasi": [
        "Waktu paling subur",
        "Tingkatkan asupan cairan",
        "Pantau suhu basal tubuh"
    ],
    "luteal": [
        "Waspada gejala PMS",
        "Kurangi konsumsi garam",
        "Tingkatkan asupan magnesium"
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        if 'last_period' in request.form:  # Jika dari period tracker
            last_period = request.form['last_period']
            cycle_length = int(request.form['cycle_length'])
            
            # Validasi input
            if cycle_length < 21 or cycle_length > 45:
                raise ValueError("Siklus haid normal antara 21-45 hari")
                
            # Hitung prediksi
            last_date = datetime.strptime(last_period, '%Y-%m-%d')
            prediction_date = last_date + timedelta(days=cycle_length)
            
            # Tentukan fase siklus
            days_passed = (datetime.now() - last_date).days
            phase = get_cycle_phase(days_passed, cycle_length)
            tips = CYCLE_TIPS.get(phase, [])
            
            return render_template('result.html', 
                               type="period",
                               prediction_date=prediction_date.strftime('%d %B %Y'),
                               cycle_phase=phase.capitalize(),
                               tips=tips)
        
        else:  # Jika dari symptoms form
            symptoms = request.form.getlist('symptoms')
            budget = request.form['drug_budget']
            
            if not symptoms:
                raise ValueError("Pilih minimal satu gejala")
            
            # Dapatkan rekomendasi obat
            recommendations = []
            for symptom in symptoms:
                if symptom in DRUG_RECOMMENDATIONS and budget in DRUG_RECOMMENDATIONS[symptom]:
                    recommendations.extend(DRUG_RECOMMENDATIONS[symptom][budget])
            
            if not recommendations:
                raise ValueError("Tidak ditemukan rekomendasi untuk gejala dan budget yang dipilih")
            
            return render_template('result.html',
                               type="drugs",
                               symptoms=symptoms,
                               budget=budget,
                               recommendations=recommendations)
    
    except ValueError as e:
        return render_template('error.html', error_message=str(e))
    except Exception as e:
        return render_template('error.html', error_message="Terjadi kesalahan sistem")

def get_cycle_phase(days_passed, cycle_length):
    """Menentukan fase siklus menstruasi"""
    if days_passed < 0:
        return "unknown"
    elif days_passed < 5:
        return "menstruasi"
    elif days_passed < 14:
        return "folikular"
    elif days_passed < 16:
        return "ovulasi"
    else:
        return "luteal"

if _name_ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
