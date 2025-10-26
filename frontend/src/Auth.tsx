import { useState } from "react";

export function AuthCard() {
  const [newUser, setUserStatus] = useState(true);
  const DisplayForm = newUser ? RegisterForm : LoginForm;
  return (
    <div className="auth-card">
      <button onClick={() => setUserStatus(!newUser)}>
        {newUser ? "Already have an account? Login" : "New user? Register"}
      </button>
      <DisplayForm />
    </div>
  );
}

function RegisterForm() {
  function register(formData: FormData) {
    const email = formData.get("email");
    const password = formData.get("password");
    const confirmed = password == formData.get("c_password");

    if (!confirmed) {
      alert("Passwords do not match");
    }
  }

  return (
    <div className="authCard">
      <form action={register}>
        <div>
          <label>Email</label>
        </div>
        <div>
          <input name="email" />
        </div>
        <div>
          <label>Password</label>
        </div>
        <div>
          <input name="password" />
        </div>
        <div>
          <label>Confirm password</label>
        </div>
        <div>
          <input name="c_password" />
        </div>
        <div>
          <button type="submit"> Sign Up</button>
        </div>
      </form>
    </div>
  );
}

function LoginForm() {
  function login(formData: FormData) {
    const email = formData.get("email");
    const password = formData.get("password");
  }

  return (
    <div className="authCard">
      <form action={login}>
        <div>
          <label>Email</label>
        </div>
        <div>
          <input name="email" />
        </div>
        <div>
          <label>Choose a password</label>
        </div>
        <div>
          <input name="password" />
        </div>
        <div>
          <button type="submit"> Log In</button>
        </div>
      </form>
    </div>
  );
}
