import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

const SUPABASE_URL = "https://stscpsybcrcownfmcmym.supabase.co";

const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_3hQL55nVMwWaQBlocB_UNA_db91X-di";

const supabase = createClient(
    SUPABASE_URL,
    SUPABASE_PUBLISHABLE_KEY
);

const loginForm = document.getElementById("login-form");
const message = document.getElementById("message");

loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    message.textContent = "Iniciando sesión...";

    const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password
    });

    if (error) {
        console.error(error);
        message.textContent = "Error: " + error.message;
        return;
    }

    console.log("Usuario autenticado:", data.user);

const { data: perfil, error: perfilError } = await supabase
    .from("profiles")
    .select("role, email")
    .eq("id", data.user.id)
    .single();

if (perfilError) {
    console.error("Error al obtener el perfil:", perfilError);
    message.textContent = "Error al obtener el perfil.";
    return;
}

console.log("Perfil:", perfil);
message.textContent = "Rol: " + perfil.role;
if (perfil.role === "admin") {
    window.location.href = "admin.html";
} else if (perfil.role === "estudiante") {
    window.location.href = "estudiante.html";
}

});

const { data: { session } } = await supabase.auth.getSession();

if (session) {

    const { data: perfil, error: perfilError } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", session.user.id)
        .single();

    if (!perfilError) {

        if (perfil.role === "admin") {
            window.location.href = "admin.html";
        } else if (perfil.role === "estudiante") {
            window.location.href = "estudiante.html";
        }
    }
}