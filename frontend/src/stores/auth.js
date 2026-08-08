import { reactive } from "vue";
import { registerUser, loginUser } from "../api/auth.js";

const state = reactive({
  token: localStorage.getItem("gp_token") || null,
  user: JSON.parse(localStorage.getItem("gp_user") || "null"),
});

function setSession(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem("gp_token", token);
  localStorage.setItem("gp_user", JSON.stringify(user));
}

function clearSession() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("gp_token");
  localStorage.removeItem("gp_user");
}

// axios không dùng res.ok như fetch — lỗi (4xx/5xx) sẽ throw, và nội dung
// lỗi backend trả về nằm ở err.response.data
function extractErrorMessage(err, fallback) {
  const body = err.response?.data;
  if (body?.errors?.length) return body.errors.join(", ");
  if (body?.error) return body.error;
  return fallback;
}

async function register({ username, email, password }) {
  try {
    const { data } = await registerUser({ username, email, password });
    setSession(data.token, data.user);
    return data.user;
  } catch (err) {
    throw new Error(extractErrorMessage(err, "Đăng ký thất bại."));
  }
}

async function login({ identifier, password }) {
  try {
    const { data } = await loginUser({ identifier, password });
    setSession(data.token, data.user);
    return data.user;
  } catch (err) {
    throw new Error(extractErrorMessage(err, "Đăng nhập thất bại."));
  }
}

function logout() {
  clearSession();
}

function isAdmin() {
  return state.user?.role === "admin";
}

export const authStore = {
  state,
  register,
  login,
  logout,
  isAdmin,
};
