<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Customer Segmentation</title>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
  <style>
    :root {
      --blue: #1a73e8;
      --blue-hover: #1557b0;
      --blue-light: #e8f0fe;
      --text-primary: #202124;
      --text-secondary: #5f6368;
      --border: #dadce0;
      --border-focus: #1a73e8;
      --bg: #f8f9fa;
      --white: #ffffff;
      --error: #d93025;
      --success: #188038;
      --shadow-sm: 0 1px 2px rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      --shadow-md: 0 1px 3px rgba(60,64,67,.3), 0 4px 8px 3px rgba(60,64,67,.15);
      --radius: 8px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Roboto', sans-serif;
      background: var(--bg);
      color: var(--text-primary);
      min-height: 100vh;
    }

    header {
      background: var(--white);
      border-bottom: 1px solid var(--border);
      position: sticky; top: 0; z-index: 100;
      padding: 0 24px;
      height: 64px;
      display: flex; align-items: center; justify-content: space-between;
    }
    .nav-brand { display: flex; align-items: center; gap: 12px; text-decoration: none; }
    .nav-brand-logo {
      width: 40px; height: 40px; border-radius: 50%;
      background: linear-gradient(135deg, #4285f4, #34a853, #fbbc04, #ea4335);
      display: grid; place-items: center;
    }
    .nav-brand-logo span { color: #fff; font-weight: 700; font-size: 18px; font-family: 'Google Sans', sans-serif; }
    .nav-title { font-family: 'Google Sans', sans-serif; font-size: 20px; color: var(--text-primary); letter-spacing: -.2px; }
    .nav-title span { color: var(--blue); }
    .avatar {
      width: 36px; height: 36px; border-radius: 50%;
      background: linear-gradient(135deg, #4285f4, #185abc);
      display: grid; place-items: center;
      color: #fff; font-size: 14px; font-weight: 500; cursor: pointer;
    }

    main { max-width: 860px; margin: 40px auto; padding: 0 16px 80px; }

    .page-header { margin-bottom: 32px; }
    .page-header h1 {
      font-family: 'Google Sans', sans-serif;
      font-size: 28px; font-weight: 400;
      color: var(--text-primary); margin-bottom: 6px;
    }
    .page-header p { color: var(--text-secondary); font-size: 14px; line-height: 1.6; }

    .progress-bar-wrap { display: flex; gap: 4px; margin-bottom: 32px; }
    .progress-seg {
      flex: 1; height: 4px; border-radius: 2px;
      background: var(--border); transition: background .3s;
    }
    .progress-seg.done { background: var(--blue); }

    .card {
      background: var(--white);
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
      margin-bottom: 20px;
      overflow: hidden;
      transition: box-shadow .2s;
    }
    .card:hover { box-shadow: var(--shadow-md); }
    .card-header {
      padding: 20px 24px 16px;
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; gap: 12px;
    }
    .card-icon {
      width: 36px; height: 36px; border-radius: 50%;
      display: grid; place-items: center; flex-shrink: 0;
    }
    .card-icon .material-icons { font-size: 20px; }
    .card-icon.blue   { background: var(--blue-light); color: var(--blue); }
    .card-icon.green  { background: #e6f4ea; color: #188038; }
    .card-icon.orange { background: #fef7e0; color: #e37400; }
    .card-icon.purple { background: #f3e8fd; color: #7b1fa2; }
    .card-title { font-family: 'Google Sans', sans-serif; font-size: 15px; font-weight: 500; color: var(--text-primary); }
    .card-subtitle { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
    .card-body { padding: 24px; }

    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .form-grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
    @media (max-width: 640px) {
      .form-grid, .form-grid.cols-3 { grid-template-columns: 1fr; }
    }

    .field { position: relative; }
    .field label {
      position: absolute; top: 50%; left: 13px;
      transform: translateY(-50%);
      font-size: 14px; color: var(--text-secondary);
      pointer-events: none;
      transition: all .18s cubic-bezier(.4,0,.2,1);
      background: var(--white);
      padding: 0 3px;
    }
    .field input, .field select {
      width: 100%; height: 52px;
      border: 1.5px solid var(--border);
      border-radius: var(--radius);
      padding: 14px 14px 0;
      font-size: 14px;
      font-family: 'Roboto', sans-serif;
      color: var(--text-primary);
      background: var(--white);
      outline: none;
      transition: border-color .18s, box-shadow .18s;
      appearance: none; -webkit-appearance: none;
    }
    .field select { padding-top: 14px; cursor: pointer; }
    .field input:focus, .field select:focus {
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(26,115,232,.12);
    }
    .field input:focus + label,
    .field input:not(:placeholder-shown) + label,
    .field select:focus + label,
    .field select.has-value + label {
      top: 8px; transform: none; font-size: 11px; color: var(--blue); font-weight: 500;
    }
    .select-wrap { position: relative; }
    .select-wrap::after {
      content: 'expand_more'; font-family: 'Material Icons';
      position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
      color: var(--text-secondary); font-size: 20px; pointer-events: none;
    }
    .field input::placeholder { color: transparent; }

    .chip-group { display: flex; gap: 8px; flex-wrap: wrap; }
    .chip {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 0 16px; height: 36px;
      border-radius: 18px; border: 1.5px solid var(--border);
      font-size: 14px; font-family: 'Google Sans', sans-serif;
      color: var(--text-secondary); cursor: pointer;
      transition: all .18s; user-select: none;
      background: var(--white);
    }
    .chip:hover { border-color: var(--blue); color: var(--blue); background: var(--blue-light); }
    .chip input[type="radio"] { display: none; }
    .chip.selected { background: var(--blue-light); border-color: var(--blue); color: var(--blue); font-weight: 500; }
    .chip.selected::before { content: 'check'; font-family: 'Material Icons'; font-size: 16px; }
    .chip-label { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500; letter-spacing: .4px; text-transform: uppercase; }

    .submit-card {
      background: var(--white); border-radius: var(--radius);
      box-shadow: var(--shadow-sm); padding: 24px;
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
      flex-wrap: wrap;
    }
    .submit-info { flex: 1; min-width: 200px; }
    .submit-info p { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-top: 4px; }
    .submit-info strong { font-family: 'Google Sans', sans-serif; font-size: 15px; color: var(--text-primary); }
    .btn-primary {
      display: inline-flex; align-items: center; gap: 8px;
      background: var(--blue); color: #fff;
      border: none; border-radius: var(--radius);
      padding: 0 24px; height: 44px;
      font-size: 14px; font-family: 'Google Sans', sans-serif; font-weight: 500;
      cursor: pointer; transition: background .2s, box-shadow .2s;
      box-shadow: 0 1px 2px rgba(0,0,0,.3);
    }
    .btn-primary:hover { background: var(--blue-hover); box-shadow: 0 2px 6px rgba(0,0,0,.3); }
    .btn-primary .material-icons { font-size: 18px; }

    .result-banner {
      border-radius: var(--radius); padding: 20px 24px;
      margin-bottom: 28px; display: flex; align-items: flex-start; gap: 16px;
      animation: slideIn .35s ease;
    }
    @keyframes slideIn { from { opacity:0; transform:translateY(-12px); } to { opacity:1; transform:none; } }
    .result-banner.cluster-0 { background: #e8f0fe; border-left: 4px solid #1a73e8; }
    .result-banner.cluster-1 { background: #e6f4ea; border-left: 4px solid #188038; }
    .result-banner.cluster-2 { background: #fef7e0; border-left: 4px solid #f29900; }
    .result-banner.cluster-3 { background: #fce8e6; border-left: 4px solid #d93025; }
    .result-icon { font-size: 28px; flex-shrink: 0; }
    .result-title { font-family: 'Google Sans', sans-serif; font-size: 18px; font-weight: 500; margin-bottom: 4px; }
    .result-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.5; }
    .result-tag {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 3px 10px; border-radius: 12px;
      font-size: 11px; font-weight: 600; letter-spacing: .5px;
      margin-top: 8px; text-transform: uppercase;
    }
    .cluster-0 .result-tag { background: #1a73e8; color: #fff; }
    .cluster-1 .result-tag { background: #188038; color: #fff; }
    .cluster-2 .result-tag { background: #f29900; color: #fff; }
    .cluster-3 .result-tag { background: #d93025; color: #fff; }

    footer { text-align: center; padding: 32px; color: var(--text-secondary); font-size: 12px; }
    footer a { color: var(--blue); text-decoration: none; }

    .section-divider { display: flex; align-items: center; gap: 12px; margin: 8px 0 4px; }
    .section-divider span { font-size: 11px; font-weight: 600; color: var(--text-secondary); letter-spacing: .8px; text-transform: uppercase; white-space: nowrap; }
    .section-divider::before, .section-divider::after { content:''; flex:1; height:1px; background: var(--border); }
  </style>
</head>
<body>

<header>
  <a class="nav-brand" href="#">
    <div class="nav-brand-logo"><span>CS</span></div>
    <span class="nav-title">Customer <span>Segmentation</span></span>
  </a>
  <div class="avatar">U</div>
</header>

<main>
  <div class="page-header">
    <h1>Predict Customer Cluster</h1>
    <p>Fill in the customer details below. Our model will classify them into the most relevant marketing segment.</p>
  </div>

  <div class="progress-bar-wrap">
    {% for i in range(20) %}<div class="progress-seg"></div>{% endfor %}
  </div>

  {% if context is not none %}
  <div class="result-banner cluster-{{ context }}">
    <div class="result-icon">
      {% if context == 0 %}💎{% endif %}
      {% if context == 1 %}🛒{% endif %}
      {% if context == 2 %}🏷️{% endif %}
      {% if context == 3 %}⏰{% endif %}
    </div>
    <div>
      <div class="result-title">Cluster {{ context }} Identified</div>
      <div class="result-desc">
        {% if context == 0 %}High Spenders — This customer responds best to premium offers and exclusive products.{% endif %}
        {% if context == 1 %}Online Shoppers — Digital coupons and flash sales drive the highest conversion.{% endif %}
        {% if context == 2 %}Value Seekers — Discount deals and bundled offers are most effective here.{% endif %}
        {% if context == 3 %}Occasional Buyers — Re-engagement campaigns and loyalty nudges are recommended.{% endif %}
      </div>
      <div class="result-tag">
        {% if context == 0 %}⭐ Premium{% endif %}
        {% if context == 1 %}🌐 Digital{% endif %}
        {% if context == 2 %}💰 Value{% endif %}
        {% if context == 3 %}🔁 Re-engage{% endif %}
      </div>
    </div>
  </div>
  {% endif %}

  <form action="/" method="post" id="segForm">

    <!-- Demographics -->
    <div class="card">
      <div class="card-header">
        <div class="card-icon blue"><span class="material-icons">person</span></div>
        <div>
          <div class="card-title">Demographics</div>
          <div class="card-subtitle">Basic personal information about the customer</div>
        </div>
      </div>
      <div class="card-body">
        <div class="form-grid">
          <div class="field">
            <input type="number" id="Age" name="Age" placeholder=" " required min="0">
            <label for="Age">Age</label>
          </div>
          <div class="field">
            <input type="number" id="Income" name="Income" placeholder=" " required min="0">
            <label for="Income">Annual Income</label>
          </div>
          <div class="field">
            <div class="select-wrap">
              <select id="Education" name="Education" required onchange="this.classList.toggle('has-value', this.value !== '')">
                <option value="" disabled selected></option>
                <option value="0">Basic</option>
                <option value="1">2nd Cycle</option>
                <option value="2">Graduation</option>
                <option value="3">Master</option>
                <option value="4">PhD</option>
              </select>
              <label for="Education">Education Level</label>
            </div>
          </div>
          <div class="field">
            <input type="number" id="Days_as_Customer" name="Days_as_Customer" placeholder=" " required min="0">
            <label for="Days_as_Customer">Days as Customer</label>
          </div>
        </div>

        <div style="margin-top:20px;">
          <div class="chip-label">Marital Status</div>
          <div class="chip-group">
            <label class="chip">
              <input type="radio" name="Marital_Status" value="0" required onchange="updateChips('Marital_Status')"> Single / Divorced
            </label>
            <label class="chip">
              <input type="radio" name="Marital_Status" value="1" onchange="updateChips('Marital_Status')"> Married / Together
            </label>
          </div>
        </div>

        <div style="margin-top:16px;">
          <div class="chip-label">Has Kids</div>
          <div class="chip-group">
            <label class="chip">
              <input type="radio" name="Parental_Status" value="0" required onchange="updateChips('Parental_Status')"> No
            </label>
            <label class="chip">
              <input type="radio" name="Parental_Status" value="1" onchange="updateChips('Parental_Status')"> Yes
            </label>
          </div>
        </div>

        <div class="field" style="margin-top:16px; max-width:260px;">
          <input type="number" id="Children" name="Children" placeholder=" " required min="0">
          <label for="Children">Number of Children</label>
        </div>
      </div>
    </div>

    <!-- Purchase Behaviour -->
    <div class="card">
      <div class="card-header">
        <div class="card-icon green"><span class="material-icons">shopping_bag</span></div>
        <div>
          <div class="card-title">Purchase Behaviour</div>
          <div class="card-subtitle">Spending patterns and product categories</div>
        </div>
      </div>
      <div class="card-body">
        <div class="section-divider"><span>Category Spend</span></div>
        <div class="form-grid cols-3" style="margin-top:16px;">
          <div class="field"><input type="number" id="Wines" name="Wines" placeholder=" " required min="0"><label for="Wines">🍷 Wines</label></div>
          <div class="field"><input type="number" id="Fruits" name="Fruits" placeholder=" " required min="0"><label for="Fruits">🍎 Fruits</label></div>
          <div class="field"><input type="number" id="Meat" name="Meat" placeholder=" " required min="0"><label for="Meat">🥩 Meat</label></div>
          <div class="field"><input type="number" id="Fish" name="Fish" placeholder=" " required min="0"><label for="Fish">🐟 Fish</label></div>
          <div class="field"><input type="number" id="Sweets" name="Sweets" placeholder=" " required min="0"><label for="Sweets">🍬 Sweets</label></div>
          <div class="field"><input type="number" id="Gold" name="Gold" placeholder=" " required min="0"><label for="Gold">🥇 Gold</label></div>
        </div>
        <div class="section-divider" style="margin-top:24px;"><span>Totals & Recency</span></div>
        <div class="form-grid" style="margin-top:16px;">
          <div class="field"><input type="number" id="Total_Spending" name="Total_Spending" placeholder=" " required min="0"><label for="Total_Spending">Total Spending</label></div>
          <div class="field"><input type="number" id="Recency" name="Recency" placeholder=" " required min="0"><label for="Recency">Days Since Last Purchase</label></div>
        </div>
      </div>
    </div>

    <!-- Channel Activity -->
    <div class="card">
      <div class="card-header">
        <div class="card-icon orange"><span class="material-icons">bar_chart</span></div>
        <div>
          <div class="card-title">Channel Activity</div>
          <div class="card-subtitle">How and where the customer shops</div>
        </div>
      </div>
      <div class="card-body">
        <div class="form-grid cols-3">
          <div class="field"><input type="number" id="Web" name="Web" placeholder=" " required min="0"><label for="Web">🌐 Web Purchases</label></div>
          <div class="field"><input type="number" id="Catalog" name="Catalog" placeholder=" " required min="0"><label for="Catalog">📄 Catalog Purchases</label></div>
          <div class="field"><input type="number" id="Store" name="Store" placeholder=" " required min="0"><label for="Store">🏪 Store Purchases</label></div>
          <div class="field"><input type="number" id="Discount_Purchases" name="Discount_Purchases" placeholder=" " required min="0"><label for="Discount_Purchases">🏷️ Discount Purchases</label></div>
          <div class="field"><input type="number" id="NumWebVisitsMonth" name="NumWebVisitsMonth" placeholder=" " required min="0"><label for="NumWebVisitsMonth">📊 Web Visits/Month</label></div>
        </div>
      </div>
    </div>

    <!-- Promotions -->
    <div class="card">
      <div class="card-header">
        <div class="card-icon purple"><span class="material-icons">campaign</span></div>
        <div>
          <div class="card-title">Promotions</div>
          <div class="card-subtitle">Campaign engagement and response rate</div>
        </div>
      </div>
      <div class="card-body">
        <div class="form-grid">
          <div class="field">
            <input type="number" id="Total_Promo" name="Total_Promo" placeholder=" " required min="0" max="5">
            <label for="Total_Promo">Accepted Promos (0–5)</label>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit -->
    <div class="submit-card">
      <div class="submit-info">
        <strong>Ready to predict?</strong>
        <p>All fields are required. Our ML model will classify this customer into the most relevant segment instantly.</p>
      </div>
      <button type="submit" class="btn-primary">
        <span class="material-icons">auto_awesome</span>
        Predict Customer Cluster
      </button>
    </div>

  </form>
</main>

<footer>
  &copy; 2024 Customer Segmentation &nbsp;·&nbsp; <a href="#">Privacy</a> &nbsp;·&nbsp; <a href="#">Terms</a>
</footer>

<script>
  function updateChips(name) {
    document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
      const chip = radio.closest('.chip');
      if (chip) chip.classList.toggle('selected', radio.checked);
    });
  }

  const allFields = document.querySelectorAll('input[required], select[required]');
  const segs = document.querySelectorAll('.progress-seg');

  function updateProgress() {
    const total = allFields.length;
    let filled = 0;
    const seen = new Set();
    allFields.forEach(f => {
      if (f.type === 'radio') {
        if (!seen.has(f.name) && document.querySelector(`input[name="${f.name}"]:checked`)) {
          filled++; seen.add(f.name);
        }
      } else if (f.value.trim() !== '') filled++;
    });
    const pct = filled / total;
    segs.forEach((seg, i) => seg.classList.toggle('done', i / segs.length < pct));
  }

  allFields.forEach(f => f.addEventListener('input', updateProgress));
  allFields.forEach(f => f.addEventListener('change', updateProgress));
  updateProgress();
</script>

</body>
</html>
