<template>
  <div id="app">
    <div class="bg-gradient"></div>

    <header class="main-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🎁</span>
          <h1 class="logo-text">Gift<span>AI</span></h1>
        </div>

        <div class="header-actions">
          <div class="auth-section">
            <div v-if="!isLoggedIn" class="auth-dropdown">
              <button class="auth-toggle-btn" @click="showAuth = !showAuth">
                {{ isRegisterMode ? 'Registracija' : 'Prijava' }} ▾
              </button>
              
              <Transition name="fade">
                <div v-if="showAuth" class="auth-popover">
                  <h4 class="auth-title">{{ isRegisterMode ? 'Stvori račun' : 'Prijava' }}</h4>
                  <div class="auth-inputs">
                    <input v-model="username" type="text" placeholder="Korisničko ime" class="auth-input">
                    <input v-if="isRegisterMode" v-model="email" type="email" placeholder="E-mail" class="auth-input">
                    <input v-model="password" type="password" placeholder="Lozinka" class="auth-input">
                  </div>
                  <button v-if="!isRegisterMode" @click="login" class="login-btn">Prijavi se</button>
                  <button v-else @click="register" class="register-btn">Registriraj se</button>
                  <p class="toggle-text" @click="isRegisterMode = !isRegisterMode">
                    {{ isRegisterMode ? 'Povratak na prijavu' : 'Nemaš račun? Registriraj se' }}
                  </p>
                </div>
              </Transition>
            </div>

            <div v-else class="profile-pill" @click="toggleProfile" style="cursor: pointer;">
              <div class="user-info">
                <div class="avatar">👤</div>
                <span class="welcome-text">{{ username }}</span>
              </div>
              <button @click.stop="logout" class="logout-btn">Odjava</button>
            </div>
          </div>

          <button class="cart-btn" @click="showCart = !showCart">
            <span class="cart-icon">🛒</span>
            <span class="cart-count" v-if="cart.length > 0">{{ cart.length }}</span>
          </button>
        </div>
      </div>
    </header>

    <main class="container">
      <Transition name="slide">
        <div v-if="showCart" class="cart-sidebar">
          <div class="cart-header">
            <h3>Vaša košarica</h3>
            <button @click="showCart = false" class="close-btn">&times;</button>
          </div>
          <div class="cart-body">
            <div v-if="cart.length === 0" class="empty-state">Prazno</div>
            <div v-for="(item, index) in cart" :key="index" class="cart-item">
              <div class="item-details">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-price">{{ item.price }} €</span>
              </div>
              <button @click="removeFromCart(index)" class="mini-remove">×</button>
            </div>
          </div>
          <div class="cart-footer" v-if="cart.length > 0">
            <div class="total-row">
              <span>Ukupno:</span>
              <span class="total-amount">{{ cartTotal }} €</span>
            </div>
            <button @click="checkout" class="checkout-btn">Plaćanje</button>
            <button @click="clearCart" class="clear-cart-btn">Isprazni</button>
          </div>
        </div>
      </Transition>
      <Transition name="fade">
          <div v-if="showProfile" class="profile-overlay">
            <div class="profile-card">
              <button class="close-profile" @click="showProfile = false">&times;</button>
              
              <div class="profile-header">
                <div class="large-avatar">👤</div>
                <h2>Korisnički Profil</h2>
                <p class="user-badge">Premium Član</p>
              </div>

              <div class="profile-content">
                <div class="info-group">
                  <label>Korisničko ime</label>
                  <div class="info-value">{{ username }}</div>
                </div>
                
                <div class="info-group">
                  <label>Status računa</label>
                  <div class="info-value active">Aktivan</div>
                </div>

                <div class="stats-grid">
                  <div class="stat-box">
                    <span class="stat-num">{{ cart.length }}</span>
                    <span class="stat-label">U košarici</span>
                  </div>
                <div class="stat-box clickable" @click="showOrdersModal = true">
                  <span class="stat-num">{{ activeOrders.length + orderHistory.length }}</span>
                  <span class="stat-label">Narudžbi ⮕</span>
                </div>
                </div>

                <div class="profile-actions">
                  <button class="edit-btn">Uredi podatke</button>
                  <button @click="logout(); showProfile = false" class="logout-full-btn">Odjavi se</button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
        <Transition name="fade">
          <div v-if="showOrdersModal" class="profile-overlay orders-overlay">
            <div class="profile-card orders-modal">
              <button class="close-profile" @click="showOrdersModal = false">&times;</button>
              
              <div class="profile-header">
                <div class="large-avatar">📦</div>
                <h2>Moje Narudžbe</h2>
              </div>

              <div class="order-tabs">
                <button :class="{ active: activeTab === 'active' }" @click="activeTab = 'active'">
                  Aktivno ({{ activeOrders.length }})
                </button>
                <button :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
                  Povijest ({{ orderHistory.length }})
                </button>
              </div>

              <div class="orders-list-detailed">
                <div v-if="activeTab === 'active'">
                  <div v-if="activeOrders.length === 0" class="no-orders">Nema aktivnih narudžbi.</div>
                  <div v-for="order in activeOrders" :key="order.id" class="order-item-detailed">
                    <div class="order-meta">
                      <span class="order-number">Narudžba #{{ order.id }}</span>
                      <span class="order-status tag-processing">U obradi</span>
                    </div>
                    <p class="order-products">{{ order.items }}</p>
                    <div class="order-price-row">
                      <span class="label">Ukupno:</span>
                      <span class="value">{{ order.total_price }} €</span>
                    </div>
                  </div>
                </div>

                <div v-if="activeTab === 'history'">
                  </div>
              </div>
            </div>
          </div>
        </Transition>

      <section class="catalog-section">
        <h2 class="section-title">Preporučeni darovi</h2>
        <div v-if="loading" class="loader-container">
          <div class="spinner"></div>
          <p>Učitavanje ponude...</p>
        </div>

        <div class="product-grid">
          <div v-for="product in products" :key="product.id" class="product-card">
            <div class="card-image">
              <span class="emoji-img">🎁</span>
              <div class="category-tag">{{ product.category }}</div>
            </div>
            <div class="card-info">
              <h3 class="product-title">{{ product.name }}</h3>
              <p class="product-desc">{{ product.description }}</p>
              <div class="card-footer">
                <span class="price">{{ product.price }} €</span>
                <button @click="addToCart(product)" class="add-to-cart-btn">Dodaj</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// --- AUTH LOGIKA ---
const username = ref('')
const password = ref('')
const email = ref('')
const isRegisterMode = ref(false)
const isLoggedIn = ref(!!localStorage.getItem('access_token'))
const showAuth = ref(false)

// NARUDŽBE (Samo jednom definiraj!)
const activeTab = ref('active')
const activeOrders = ref([])
const orderHistory = ref([])
const showOrdersModal = ref(false)

const login = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/login/', {
      username: username.value,
      password: password.value
    })
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    isLoggedIn.value = true
    showAuth.value = false
    
    // ODMAH NAKON LOGIN-A DOHVATI NARUDŽBE
    await fetchOrders(); 
    
  } catch (error) {
    alert("Greška pri prijavi")
  }
}

const register = async () => {
  try {
    await axios.post('http://127.0.0.1:8000/api/register/', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    alert("Registracija uspješna!")
    isRegisterMode.value = false
  } catch (error) {
    alert("Greška pri registraciji")
  }
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  isLoggedIn.value = false
  username.value = ''
}

const showProfile = ref(false) // Kontrola vidljivosti profila

// Funkcija za zatvaranje profila i otvaranje košarice ako treba
const toggleProfile = () => {
  showProfile.value = !showProfile.value
  if (showProfile.value) showCart.value = false // Zatvori košaricu ako otvaraš profil
}

const fetchOrders = async () => {
  if (!isLoggedIn.value) return;
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get('http://127.0.0.1:8000/api/orders/my-orders/', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    // Filtriramo narudžbe na aktivne i povijest radi prikaza u profilu
    // Za sada sve nove stavljamo u 'activeOrders', a stare u 'orderHistory'
    activeOrders.value = response.data.filter(o => o.status === 'U obradi');
    orderHistory.value = response.data.filter(o => o.status === 'Dostavljeno');
  } catch (error) {
    console.error("Greška pri dohvaćanju narudžbi:", error);
  }
};

const checkout = async () => {
  if (cart.value.length === 0) return;
  try {
    const token = localStorage.getItem('access_token');
    const orderData = {
      items: cart.value.map(item => item.name).join(", "),
      total: cartTotal.value
    };

    await axios.post('http://127.0.0.1:8000/api/orders/create/', orderData, {
      headers: { Authorization: `Bearer ${token}` }
    });

    alert("Narudžba je uspješno poslana!");
    cart.value = [];
    showCart.value = false;
    
    // OSVJEŽI PROFIL NAKON KUPNJE
    await fetchOrders(); 
    
  } catch (error) {
    alert("Morate biti prijavljeni za kupnju!");
    showAuth.value = true;
  }
};

// --- KATALOG & KOŠARICA LOGIKA ---
const products = ref([])
const cart = ref([])
const loading = ref(true)
const showCart = ref(false)

const fetchProducts = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/products/')
    products.value = response.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const addToCart = (product) => cart.value.push(product)
const removeFromCart = (index) => cart.value.splice(index, 1)
const clearCart = () => { if(confirm("Isprazniti?")) cart.value = [] }
const cartTotal = computed(() => cart.value.reduce((acc, item) => acc + parseFloat(item.price), 0).toFixed(2))

onMounted(() => {
  fetchProducts();
  // AKO JE KORISNIK VEĆ PRIJAVLJEN PRI UČITAVANJU
  if (isLoggedIn.value) {
    fetchOrders();
  }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

/* --- PROFIL OVERLAY --- */
.profile-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(10px);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-card {
  background: #1e293b;
  width: 90%;
  max-width: 500px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 3rem 2rem;
  position: relative;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.close-profile {
  position: absolute;
  top: 20px; right: 20px;
  background: none; border: none;
  color: #94a3b8; font-size: 2rem;
  cursor: pointer;
}

.profile-header {
  text-align: center;
  margin-bottom: 2rem;
}

.large-avatar {
  width: 80px; height: 80px;
  background: #42b983;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 2.5rem;
  margin: 0 auto 1rem;
}

.user-badge {
  color: #42b983;
  background: rgba(66, 185, 131, 0.1);
  display: inline-block;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 700;
}

.info-group {
  margin-bottom: 1.5rem;
}

.info-group label {
  display: block;
  color: #94a3b8;
  font-size: 0.8rem;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.info-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #f8fafc;
}

.info-value.active { color: #42b983; }

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 2rem 0;
}

.stat-box {
  background: rgba(15, 23, 42, 0.5);
  padding: 1rem;
  border-radius: 15px;
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  color: #42b983;
}

.stat-label {
  font-size: 0.8rem;
  color: #94a3b8;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.edit-btn {
  background: white; color: #0f172a;
  border: none; padding: 1rem; border-radius: 12px;
  font-weight: 800; cursor: pointer;
}

.logout-full-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 1rem; border-radius: 12px;
  font-weight: 700; cursor: pointer;
}

#app {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background-color: #0f172a;
  color: #f8fafc;
  min-height: 100vh;
  padding-bottom: 50px;
}

.main-header {
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(15px);
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  position: sticky; top: 0; z-index: 1000;
}

.header-content {
  max-width: 1200px; margin: 0 auto;
  display: flex; justify-content: space-between; align-items: center;
}

.header-actions { display: flex; align-items: center; gap: 20px; }

.logo { display: flex; align-items: center; gap: 10px; }
.logo-text { font-weight: 800; font-size: 1.4rem; }
.logo-text span { color: #42b983; }

/* AUTH POP-OVER DIZAJN */
.auth-dropdown { position: relative; }
.auth-toggle-btn {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  color: white; padding: 0.6rem 1rem; border-radius: 10px; cursor: pointer;
}

.auth-popover {
  position: absolute; top: 50px; right: 0; width: 280px;
  background: #1e293b; border: 1px solid rgba(255,255,255,0.1);
  padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.auth-input {
  width: 100%; background: #0f172a; border: 1px solid #334155;
  padding: 0.7rem; border-radius: 8px; color: white; margin-bottom: 10px;
  box-sizing: border-box;
}

.login-btn, .register-btn {
  width: 100%; background: #42b983; color: #0f172a; border: none;
  padding: 0.7rem; border-radius: 8px; font-weight: bold; cursor: pointer;
}

.profile-pill {
  display: flex; align-items: center; gap: 15px;
  background: rgba(66, 185, 131, 0.1); padding: 0.4rem 0.8rem; border-radius: 50px;
}

.user-info { display: flex; align-items: center; gap: 8px; }
.avatar { background: #42b983; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; }
.logout-btn { background: none; border: none; color: #ff6b6b; cursor: pointer; font-size: 0.8rem; text-decoration: underline; }

/* KATALOG */
.product-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem; max-width: 1200px; margin: 0 auto; padding: 0 20px;
}

.product-card {
  background: #1e293b; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);
  transition: 0.3s;
}
.product-card:hover { transform: translateY(-5px); border-color: #42b983; }

.card-image {
  background: #334155; height: 160px; display: flex; align-items: center;
  justify-content: center; font-size: 3rem; border-radius: 20px 20px 0 0; position: relative;
}

.category-tag {
  position: absolute; top: 12px; left: 12px; background: #42b983;
  color: #0f172a; font-size: 0.6rem; font-weight: 800; padding: 3px 8px; border-radius: 4px;
}

.card-info { padding: 1.5rem; }
.product-title { margin: 0; font-size: 1.2rem; }
.product-desc { color: #94a3b8; font-size: 0.85rem; margin: 10px 0; height: 40px; }

.card-footer { display: flex; justify-content: space-between; align-items: center; }
.price { font-weight: 800; color: #42b983; }

.add-to-cart-btn {
  background: #42b983; border: none; padding: 0.5rem 1rem; border-radius: 8px;
  color: #0f172a; font-weight: 700; cursor: pointer;
}

/* --- MODERNIZIRANA KOŠARICA SIDEBAR --- */
.cart-sidebar {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px; /* Malo šira za bolju preglednost */
  height: 100vh;
  background: #111827; /* Tamnija nijansa za kontrast */
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
  z-index: 2000;
  padding: 2rem;
  display: flex;
  flex-direction: column;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 1rem;
}

.cart-header h3 {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
  color: #f8fafc;
}

.close-btn {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: white;
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.3s;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.cart-body {
  flex-grow: 1;
  overflow-y: auto;
  max-height: 400px;
  padding-right: 10px;
  margin-bottom: 1rem;
}

/* Stil za pojedinačni artikl u košarici */
.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 41, 59, 0.5);
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: 0.2s;
}

.cart-item:hover {
  border-color: rgba(66, 185, 131, 0.4);
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-weight: 600;
  font-size: 1rem;
  color: #f8fafc;
}

.item-price {
  color: #42b983;
  font-weight: 700;
  font-size: 0.9rem;
}

.mini-remove {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: 0.3s;
}

.mini-remove:hover {
  background: #ef4444;
  color: white;
}

/* Footer s totalom i gumbima */
.cart-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.total-row span:first-child {
  color: #94a3b8;
  font-size: 1.1rem;
}

.total-amount {
  font-size: 1.6rem;
  font-weight: 800;
  color: #42b983;
}

.checkout-btn {
  width: 100%;
  background: #42b983;
  color: #0f172a;
  padding: 1rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 800;
  border: none;
  cursor: pointer;
  margin-bottom: 0.8rem;
  transition: 0.3s;
}

.checkout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(66, 185, 131, 0.2);
}

.clear-cart-btn {
  width: 100%;
  background: transparent;
  color: #94a3b8;
  padding: 0.8rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}

.clear-cart-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.2);
}

/* Scrollbar stil za body košarice */
.cart-body::-webkit-scrollbar {
  width: 6px;
}
.cart-body::-webkit-scrollbar-thumb {
  background: rgba(66, 185, 131, 0.3);
  border-radius: 10px;
}

/* --- TABOVI I LISTA NARUDŽBI --- */
.order-tabs {
  display: flex;
  gap: 10px;
  margin-top: 1.5rem;
  background: rgba(15, 23, 42, 0.4);
  padding: 5px;
  border-radius: 12px;
}

.order-tabs button {
  flex: 1;
  padding: 8px;
  border: none;
  background: none;
  color: #94a3b8;
  cursor: pointer;
  font-weight: 600;
  border-radius: 8px;
  transition: 0.3s;
}

.order-tabs button.active {
  background: #42b983;
  color: #0f172a;
}

.orders-list {
  margin-top: 1rem;
  max-height: 250px;
  overflow-y: auto;
  padding-right: 5px;
}

.order-card-mini {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
}

.order-header-mini {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.order-id { font-weight: 800; font-size: 0.9rem; }

.order-items-text {
  font-size: 0.85rem;
  color: #cbd5e1;
  margin: 5px 0;
}

.order-status {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.tag-processing { background: rgba(234, 179, 8, 0.2); color: #eab308; }
.tag-delivered { background: rgba(66, 185, 131, 0.2); color: #42b983; }

.no-orders {
  text-align: center;
  padding: 20px;
  color: #64748b;
  font-style: italic;
  font-size: 0.9rem;
}

/* Klikabilni stat-box */
.stat-box.clickable {
  cursor: pointer;
  transition: 0.3s;
  border: 1px solid rgba(66, 185, 131, 0.2);
}
.stat-box.clickable:hover {
  background: rgba(66, 185, 131, 0.1);
  transform: translateY(-3px);
}

/* Modal za narudžbe */
.orders-modal {
  max-width: 600px; /* Malo širi od profila */
  max-height: 80vh;
  overflow-y: auto;
}

.order-item-detailed {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.order-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.order-number { font-weight: 800; color: #f8fafc; }

.order-products {
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
}

.order-price-row {
  display: flex;
  justify-content: space-between;
  font-weight: 700;
}
.order-price-row .value { color: #42b983; font-size: 1.1rem; }


/* Animacije */
.slide-enter-active, .slide-leave-active { transition: 0.4s; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
.fade-enter-active, .fade-leave-active { transition: 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>