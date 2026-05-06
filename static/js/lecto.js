(function () {
    const STORAGE_KEY = "lectoProfile";
    const PROFILE_DATA_VERSION = "launch-clean-2";
    const AVATAR_ART_VERSION = "avatar-classic-5";
    const DEFAULT_PROFILE = {
        name: "Leitor Lecto",
        points: 0,
        readTexts: {},
        favorites: {},
        quizRewards: {},
        avatarLayers: {
            base_body: null,
            body_style: null,
            hair_style: null,
            outfit: null,
            eyes: null,
            accessories: [],
        },
        avatarUnlocks: {},
        profileDataVersion: PROFILE_DATA_VERSION,
        avatarArtVersion: AVATAR_ART_VERSION,
        avatar: {
            skin: "#f0c9a2",
            hair: "#1c4259",
            hairStyle: "waves",
            outfit: "#1c4259",
            accessory: "glasses",
            expression: "smile",
            backdrop: "library",
        },
    };

    const RANKS = [
        { min: 0, name: "Leitor novo" },
        { min: 50, name: "Aprendiz atento" },
        { min: 150, name: "Explorador de textos" },
        { min: 300, name: "Leitor consistente" },
        { min: 600, name: "Mestre Lecto" },
    ];

    function cloneDefaultProfile() {
        return JSON.parse(JSON.stringify(DEFAULT_PROFILE));
    }

    function loadProfile() {
        try {
            const stored = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
            if (stored.profileDataVersion !== PROFILE_DATA_VERSION) {
                const freshProfile = cloneDefaultProfile();
                freshProfile.pendingAvatarPreset = "masculino";
                localStorage.setItem(STORAGE_KEY, JSON.stringify(freshProfile));
                return freshProfile;
            }

            const profile = cloneDefaultProfile();
            const merged = Object.assign(profile, stored, {
                avatar: Object.assign(profile.avatar, stored.avatar || {}),
                readTexts: Object.assign(profile.readTexts, stored.readTexts || {}),
                favorites: Object.assign(profile.favorites, stored.favorites || {}),
                quizRewards: Object.assign(profile.quizRewards, stored.quizRewards || {}),
                avatarLayers: normalizeAvatarLayers(stored.avatarLayers || profile.avatarLayers),
                avatarUnlocks: Object.assign(profile.avatarUnlocks, stored.avatarUnlocks || {}),
            });
            if (merged.avatarArtVersion !== AVATAR_ART_VERSION) {
                merged.avatarLayers = cloneDefaultProfile().avatarLayers;
                merged.avatarUnlocks = {};
                merged.avatarArtVersion = AVATAR_ART_VERSION;
                merged.pendingAvatarPreset = "masculino";
                localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
            }
            return merged;
        } catch (error) {
            return cloneDefaultProfile();
        }
    }

    function normalizeAvatarLayers(layers) {
        const defaults = cloneDefaultProfile().avatarLayers;
        return {
            base_body: layers.base_body || defaults.base_body,
            body_style: layers.body_style || defaults.body_style,
            hair_style: layers.hair_style || defaults.hair_style,
            outfit: layers.outfit || defaults.outfit,
            eyes: layers.eyes || defaults.eyes,
            accessories: Array.isArray(layers.accessories) ? layers.accessories : [],
        };
    }

    function saveProfile(profile) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
        renderProfile(profile);
    }

    function applyServerProfile(profile, root) {
        if (!root || root.dataset.serverAuthenticated !== "true") return profile;
        profile.points = Number(root.dataset.serverPoints || "0");
        profile.serverReadCount = Number(root.dataset.serverReadCount || "0");
        profile.readingStreak = Number(root.dataset.serverStreak || "0");
        profile.avatarUnlocks = {};
        profile.avatarArtVersion = AVATAR_ART_VERSION;
        return profile;
    }

    function getCsrfToken() {
        const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
    }

    function renderProfile(profile) {
        renderPoints(profile);
        renderAvatar(profile);
        renderAvatarStats(profile);
        renderProfileLists(profile);
        syncFavoriteButtons(profile);
    }

    function renderPoints(profile) {
        document.querySelectorAll("[data-points-total]").forEach((node) => {
            node.textContent = profile.points || 0;
        });
    }

    function getRank(points) {
        return RANKS.reduce((active, rank) => (points >= rank.min ? rank : active), RANKS[0]);
    }

    function getNextRank(points) {
        return RANKS.find((rank) => rank.min > points) || null;
    }

    function renderAvatarStats(profile) {
        const points = profile.points || 0;
        const readCount = Math.max(Number(profile.serverReadCount || 0), Object.keys(profile.readTexts || {}).length);
        const favoriteCount = Object.keys(profile.favorites || {}).length;
        const rank = getRank(points);
        const nextRank = getNextRank(points);

        document.querySelectorAll("[data-avatar-read-count]").forEach((node) => {
            node.textContent = readCount;
        });
        document.querySelectorAll("[data-avatar-favorite-count]").forEach((node) => {
            node.textContent = favoriteCount;
        });
        document.querySelectorAll("[data-avatar-rank]").forEach((node) => {
            node.textContent = rank.name;
        });
        document.querySelectorAll("[data-avatar-progress]").forEach((node) => {
            const min = rank.min;
            const max = nextRank ? nextRank.min : Math.max(points, rank.min + 1);
            const percent = Math.min(100, Math.round(((points - min) / (max - min)) * 100));
            node.style.width = `${percent}%`;
        });
    }

    function makeProfileLink(item) {
        const link = document.createElement("a");
        link.className = "profile-list__item";
        link.href = item.url || "#";

        const title = document.createElement("strong");
        title.textContent = item.title || "Texto Lecto";

        const meta = document.createElement("span");
        const date = item.readAt || item.favoritedAt;
        meta.textContent = date ? new Date(date).toLocaleDateString("pt-BR") : "Salvo neste navegador";

        link.append(title, meta);
        return link;
    }

    function renderProfileLists(profile) {
        const readsRoot = document.querySelector("[data-avatar-reads]");
        const favoritesRoot = document.querySelector("[data-avatar-favorites]");

        if (readsRoot) {
            const reads = Object.values(profile.readTexts || {}).reverse().slice(0, 6);
            readsRoot.replaceChildren();
            if (!reads.length) {
                readsRoot.append(emptyText("As leituras marcadas aparecem aqui."));
            } else {
                reads.forEach((item) => readsRoot.append(makeProfileLink(item)));
            }
        }

        if (favoritesRoot) {
            const favorites = Object.values(profile.favorites || {}).reverse().slice(0, 8);
            favoritesRoot.replaceChildren();
            if (!favorites.length) {
                favoritesRoot.append(emptyText("Textos favoritados aparecem aqui."));
            } else {
                favorites.forEach((item) => favoritesRoot.append(makeProfileLink(item)));
            }
        }
    }

    function emptyText(message) {
        const node = document.createElement("p");
        node.className = "empty-state";
        node.textContent = message;
        return node;
    }

    function showToast(message) {
        let toast = document.querySelector("[data-lecto-toast]");
        if (!toast) {
            toast = document.createElement("div");
            toast.dataset.lectoToast = "true";
            toast.className = "lecto-toast";
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.classList.add("is-visible");
        window.setTimeout(() => toast.classList.remove("is-visible"), 2600);
    }

    function setupReadingPoints() {
        const button = document.querySelector("[data-read-complete]");
        if (!button) return;

        const profile = loadProfile();
        const slug = button.dataset.textSlug;
        if (profile.readTexts && profile.readTexts[slug]) {
            button.textContent = "Texto ja marcado como lido";
            button.disabled = true;
        }

        button.addEventListener("click", () => {
            const current = loadProfile();
            current.readTexts = current.readTexts || {};
            if (current.readTexts[slug]) {
                showToast("Este texto ja rendeu pontos de leitura.");
                return;
            }
            current.readTexts[slug] = {
                title: button.dataset.textTitle,
                url: button.dataset.textUrl || window.location.pathname,
                readAt: new Date().toISOString(),
            };
            current.points = (current.points || 0) + 5;
            saveProfile(current);
            button.textContent = "Texto marcado como lido";
            button.disabled = true;
            showToast("+5 moedinhas por leitura concluida.");
        });
    }

    function setupFavoriteButtons() {
        const buttons = document.querySelectorAll("[data-favorite-toggle]");
        if (!buttons.length) return;

        syncFavoriteButtons(loadProfile());

        buttons.forEach((button) => {
            button.addEventListener("click", () => {
                const current = loadProfile();
                const slug = button.dataset.textSlug;
                current.favorites = current.favorites || {};

                if (current.favorites[slug]) {
                    delete current.favorites[slug];
                    saveProfile(current);
                    showToast("Texto removido dos favoritos.");
                } else {
                    current.favorites[slug] = {
                        title: button.dataset.textTitle,
                        url: button.dataset.textUrl || window.location.pathname,
                        favoritedAt: new Date().toISOString(),
                    };
                    saveProfile(current);
                    showToast("Texto salvo nos favoritos.");
                }
            });
        });
    }

    function syncFavoriteButtons(profile) {
        document.querySelectorAll("[data-favorite-toggle]").forEach((button) => {
            const isFavorite = Boolean(profile.favorites && profile.favorites[button.dataset.textSlug]);
            button.textContent = isFavorite ? "Remover favorito" : "Favoritar";
            button.classList.toggle("is-active", isFavorite);
        });
    }

    function setupQuizReward() {
        const panel = document.querySelector("[data-quiz-result]");
        if (!panel) return;

        const profile = loadProfile();
        const slug = panel.dataset.textSlug;
        const points = Number(panel.dataset.points || "0");
        profile.quizRewards = profile.quizRewards || {};

        if (!profile.quizRewards[slug]) {
            profile.quizRewards[slug] = {
                points,
                answeredAt: new Date().toISOString(),
            };
            profile.points = (profile.points || 0) + points;
            saveProfile(profile);
            if (points > 0) showToast(`+${points} moedinhas pelo quiz.`);
        }
    }

    function setupAvatarPage() {
        const page = document.querySelector("[data-avatar-page]");
        if (!page) return;

        const form = page.querySelector("[data-avatar-form]");
        const profile = applyServerProfile(loadProfile(), page);
        setupLayeredAvatar(page, profile);
        renderProfile(profile);

        if (!form) return;

        hydrateAvatarForm(form, profile);

        form.addEventListener("input", () => {
            const draft = profileFromForm(form, loadProfile());
            renderAvatar(draft);
        });

        form.addEventListener("submit", (event) => {
            event.preventDefault();
            const next = profileFromForm(form, loadProfile());
            saveProfile(next);
            showToast("Avatar salvo neste navegador.");
        });
    }

    function hydrateAvatarForm(form, profile) {
        const avatar = profile.avatar || DEFAULT_PROFILE.avatar;
        form.elements.namedItem("name").value = profile.name || DEFAULT_PROFILE.name;
        form.elements.namedItem("skin").value = avatar.skin || DEFAULT_PROFILE.avatar.skin;
        form.elements.namedItem("hair").value = avatar.hair || DEFAULT_PROFILE.avatar.hair;
        form.elements.namedItem("hairStyle").value = avatar.hairStyle || DEFAULT_PROFILE.avatar.hairStyle;
        form.elements.namedItem("outfit").value = avatar.outfit || DEFAULT_PROFILE.avatar.outfit;
        form.elements.namedItem("accessory").value = avatar.accessory || DEFAULT_PROFILE.avatar.accessory;
        form.elements.namedItem("expression").value = avatar.expression || DEFAULT_PROFILE.avatar.expression;
        form.elements.namedItem("backdrop").value = avatar.backdrop || DEFAULT_PROFILE.avatar.backdrop;
    }

    function profileFromForm(form, baseProfile) {
        return Object.assign({}, baseProfile, {
            name: form.elements.namedItem("name").value.trim() || DEFAULT_PROFILE.name,
            avatar: {
                skin: form.elements.namedItem("skin").value,
                hair: form.elements.namedItem("hair").value,
                hairStyle: form.elements.namedItem("hairStyle").value,
                outfit: form.elements.namedItem("outfit").value,
                accessory: form.elements.namedItem("accessory").value,
                expression: form.elements.namedItem("expression").value,
                backdrop: form.elements.namedItem("backdrop").value,
            },
        });
    }

    function renderAvatar(profile) {
        const avatar = profile.avatar || DEFAULT_PROFILE.avatar;

        document.querySelectorAll("[data-avatar-name-display]").forEach((node) => {
            node.textContent = profile.name || DEFAULT_PROFILE.name;
        });

        document.querySelectorAll("[data-avatar-preview]").forEach((preview) => {
            preview.style.setProperty("--avatar-skin", avatar.skin || DEFAULT_PROFILE.avatar.skin);
            preview.style.setProperty("--avatar-hair", avatar.hair || DEFAULT_PROFILE.avatar.hair);
            preview.style.setProperty("--avatar-outfit", avatar.outfit || DEFAULT_PROFILE.avatar.outfit);
            preview.dataset.accessory = avatar.accessory || DEFAULT_PROFILE.avatar.accessory;
            preview.dataset.expression = avatar.expression || DEFAULT_PROFILE.avatar.expression;
            preview.dataset.backdrop = avatar.backdrop || DEFAULT_PROFILE.avatar.backdrop;
            preview.dataset.hairStyle = avatar.hairStyle || DEFAULT_PROFILE.avatar.hairStyle;
        });

        renderLayeredAvatar(profile);
    }

    function avatarOptionFromNode(node) {
        return {
            id: node.dataset.optionId,
            type: node.dataset.optionType,
            name: node.dataset.optionName,
            price: Number(node.dataset.optionPrice || "0"),
            serverUnlocked: node.dataset.optionUnlocked === "true",
            canUnlock: node.dataset.optionCanUnlock === "true",
            coinsMissing: Number(node.dataset.optionCoinsMissing || "0"),
            readsMissing: Number(node.dataset.optionReadsMissing || "0"),
            requirement: node.dataset.optionRequirement || "",
            purchaseUrl: node.dataset.optionPurchaseUrl || "",
            layerOrder: Number(node.dataset.optionLayerOrder || "0"),
            asset: node.dataset.optionAsset || "",
            node,
        };
    }

    function getAvatarOptions(root) {
        return Array.from(root.querySelectorAll("[data-avatar-option]")).map(avatarOptionFromNode);
    }

    function isAvatarOptionUnlocked(profile, option) {
        const freeWithoutRequirement = option.price === 0 && !option.requirement && option.readsMissing === 0;
        return option.serverUnlocked || freeWithoutRequirement || Boolean(profile.avatarUnlocks && profile.avatarUnlocks[option.id]);
    }

    function unavailableMessage(option) {
        if (option.readsMissing > 0) {
            return `${option.name} indisponivel: faltam ${option.readsMissing} leitura(s) em ${option.requirement || "categoria exigida"}.`;
        }
        if (option.coinsMissing > 0) {
            return `Faltam ${option.coinsMissing} moedas para liberar ${option.name}.`;
        }
        return `${option.name} ainda esta indisponivel.`;
    }

    function purchaseAvatarOption(option, current) {
        if (!option.purchaseUrl) return Promise.reject(new Error("Compra indisponivel."));
        return fetch(option.purchaseUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
        })
            .then((response) =>
                response.json().then((data) => {
                    if (!response.ok || !data.ok) {
                        throw new Error(data.error || "Nao foi possivel liberar este item.");
                    }
                    return data;
                })
            )
            .then((data) => {
                current.points = data.coin_balance !== undefined ? Number(data.coin_balance) : Number(current.points || 0);
                current.avatarUnlocks[option.id] = {
                    unlockedAt: data.unlocked_at || new Date().toISOString(),
                    price: option.price,
                };
                option.serverUnlocked = true;
                option.canUnlock = true;
                option.coinsMissing = 0;
                option.node.dataset.optionUnlocked = "true";
                option.node.dataset.optionCanUnlock = "true";
                option.node.dataset.optionCoinsMissing = "0";
                return current;
            });
    }

    function selectAvatarOption(profile, option) {
        if (option.type === "accessory") {
            const selected = new Set(profile.avatarLayers.accessories || []);
            if (selected.has(option.id)) {
                selected.delete(option.id);
            } else {
                selected.add(option.id);
            }
            profile.avatarLayers.accessories = Array.from(selected);
        } else {
            profile.avatarLayers[option.type] = option.id;
        }
    }

    function findUnlockedOption(options, profile, type, names) {
        const normalizedNames = names.map((name) => name.toLowerCase());
        return options.find(
            (option) =>
                option.type === type &&
                normalizedNames.includes((option.name || "").toLowerCase()) &&
                isAvatarOptionUnlocked(profile, option)
        );
    }

    function applyAvatarPreset(builder, profile, preset) {
        const options = getAvatarOptions(builder);
        const presets = {
            masculino: {
                base_body: ["Base clara", "Base media"],
                body_style: ["Masculino"],
                hair_style: ["Cabelo azul curto", "Cabelo castanho curto", "Careca estiloso"],
                outfit: ["Blusa Lecto", "Camisa turquesa"],
                eyes: ["Olhos curiosos", "Olhos felizes"],
                accessories: ["Oculos redondo"],
            },
            feminino: {
                base_body: ["Base clara", "Base quente"],
                body_style: ["Feminino"],
                hair_style: ["Cabelo preto longo", "Cabelo laranja longo"],
                outfit: ["Casaco coral", "Camisa turquesa"],
                eyes: ["Olhos felizes", "Piscadinha"],
                accessories: ["Brinco dourado"],
            },
        };
        const selectedPreset = presets[preset];
        if (!selectedPreset) return false;

        ["base_body", "body_style", "hair_style", "outfit", "eyes"].forEach((type) => {
            const option = findUnlockedOption(options, profile, type, selectedPreset[type] || []);
            if (option) profile.avatarLayers[type] = option.id;
        });

        profile.avatarLayers.accessories = (selectedPreset.accessories || [])
            .map((name) => findUnlockedOption(options, profile, "accessory", [name]))
            .filter(Boolean)
            .map((option) => option.id);

        return true;
    }

    function ensureAvatarLayerDefaults(root, profile) {
        profile.avatarLayers = normalizeAvatarLayers(profile.avatarLayers || {});
        profile.avatarUnlocks = profile.avatarUnlocks || {};

        const options = getAvatarOptions(root);
        ["base_body", "body_style", "hair_style", "outfit", "eyes"].forEach((type) => {
            const selectedExists = options.some(
                (option) => option.type === type && option.id === profile.avatarLayers[type] && isAvatarOptionUnlocked(profile, option)
            );
            if (selectedExists) return;
            const unlockedOption = options.find((option) => option.type === type && isAvatarOptionUnlocked(profile, option));
            const firstOption = options.find((option) => option.type === type);
            profile.avatarLayers[type] = (unlockedOption || firstOption || {}).id || null;
        });
        profile.avatarLayers.accessories = (profile.avatarLayers.accessories || []).filter((id) =>
            options.some((option) => option.type === "accessory" && option.id === id && isAvatarOptionUnlocked(profile, option))
        );
    }

    function setupLayeredAvatar(page, profile) {
        const builder = page.matches("[data-avatar-builder]") ? page : page.querySelector("[data-avatar-builder]");
        if (!builder) return;

        ensureAvatarLayerDefaults(builder, profile);
        if (profile.pendingAvatarPreset && applyAvatarPreset(builder, profile, profile.pendingAvatarPreset)) {
            delete profile.pendingAvatarPreset;
            saveProfile(profile);
        }
        if (!localStorage.getItem(STORAGE_KEY)) {
            saveProfile(profile);
        }

        builder.querySelectorAll("[data-avatar-option]").forEach((button) => {
            button.addEventListener("click", () => {
                const current = loadProfile();
                ensureAvatarLayerDefaults(builder, current);
                const option = avatarOptionFromNode(button);

                if (!isAvatarOptionUnlocked(current, option)) {
                    if (!option.canUnlock) {
                        showToast(unavailableMessage(option));
                        return;
                    }
                    purchaseAvatarOption(option, current)
                        .then((updated) => {
                            showToast(`${option.name} liberado por ${option.price} moedas.`);
                            selectAvatarOption(updated, option);
                            saveProfile(updated);
                            markAvatarSaveState(builder, "dirty");
                        })
                        .catch((error) => showToast(error.message));
                    return;
                }

                selectAvatarOption(current, option);
                saveProfile(current);
                markAvatarSaveState(builder, "dirty");
            });
        });

        const saveButton = builder.querySelector("[data-avatar-save]");
        if (saveButton) {
            saveButton.addEventListener("click", () => {
                saveProfile(loadProfile());
                markAvatarSaveState(builder, "saved");
                showToast("Avatar salvo.");
            });
        }

        const resetButton = builder.querySelector("[data-avatar-reset]");
        if (resetButton) {
            resetButton.addEventListener("click", () => {
                const current = loadProfile();
                current.avatarLayers = cloneDefaultProfile().avatarLayers;
                current.avatarArtVersion = AVATAR_ART_VERSION;
                ensureAvatarLayerDefaults(builder, current);
                saveProfile(current);
                markAvatarSaveState(builder, "dirty");
                showToast("Avatar resetado para os itens gratuitos.");
            });
        }

        builder.querySelectorAll("[data-avatar-preset]").forEach((button) => {
            button.addEventListener("click", () => {
                const current = loadProfile();
                ensureAvatarLayerDefaults(builder, current);
                if (applyAvatarPreset(builder, current, button.dataset.avatarPreset)) {
                    saveProfile(current);
                    markAvatarSaveState(builder, "dirty");
                    showToast(`Preset ${button.textContent.trim()} aplicado.`);
                }
            });
        });

        const randomButton = builder.querySelector("[data-avatar-random]");
        if (randomButton) {
            randomButton.addEventListener("click", () => {
                const current = loadProfile();
                ensureAvatarLayerDefaults(builder, current);
                const options = getAvatarOptions(builder).filter((option) => isAvatarOptionUnlocked(current, option));
                ["base_body", "body_style", "hair_style", "outfit", "eyes"].forEach((type) => {
                    const choices = options.filter((option) => option.type === type);
                    if (choices.length) {
                        current.avatarLayers[type] = choices[Math.floor(Math.random() * choices.length)].id;
                    }
                });
                const accessoryChoices = options.filter((option) => option.type === "accessory");
                current.avatarLayers.accessories = accessoryChoices
                    .filter(() => Math.random() > 0.55)
                    .slice(0, 2)
                    .map((option) => option.id);
                saveProfile(current);
                markAvatarSaveState(builder, "dirty");
                showToast("Combinacao aleatoria aplicada.");
            });
        }

        renderLayeredAvatar(profile);
        markAvatarSaveState(builder, "idle");
    }

    function markAvatarSaveState(builder, state) {
        const saveButton = builder.querySelector("[data-avatar-save]");
        const status = builder.querySelector("[data-avatar-save-status]");
        if (!saveButton || !status) return;

        status.classList.toggle("is-dirty", state === "dirty");
        status.classList.toggle("is-saved", state === "saved");

        if (state === "dirty") {
            saveButton.disabled = false;
            status.textContent = "Alteracoes pendentes. Clique em Salvar avatar.";
        } else if (state === "saved") {
            saveButton.disabled = true;
            status.textContent = "Avatar salvo.";
        } else {
            saveButton.disabled = true;
            status.textContent = "Escolha uma peca para alterar o avatar.";
        }
    }

    function selectedAvatarParts(profile, byId) {
        const layers = profile.avatarLayers || {};
        return {
            base: byId.get(layers.base_body) || {},
            body: byId.get(layers.body_style) || {},
            hair: byId.get(layers.hair_style) || {},
            outfit: byId.get(layers.outfit) || {},
            eyes: byId.get(layers.eyes) || {},
            accessories: (layers.accessories || []).map((id) => byId.get(id)).filter(Boolean),
        };
    }

    function optionName(option) {
        return (option && option.name ? option.name : "").toLowerCase();
    }

    function avatarPalette(parts) {
        const base = optionName(parts.base);
        const body = optionName(parts.body);
        const outfit = optionName(parts.outfit);
        const hair = optionName(parts.hair);
        const female = body.includes("feminino");

        let skin = "#f2b981";
        let shade = "#a56543";
        if (base.includes("media")) {
            skin = "#c77c55";
            shade = "#8d4f37";
        } else if (base.includes("escura")) {
            skin = "#774534";
            shade = "#4b2b23";
        } else if (base.includes("quente")) {
            skin = "#b96d4a";
            shade = "#7d432f";
        } else if (base.includes("dourada")) {
            skin = "#d8a25f";
            shade = "#9a6532";
        }

        let shirt = female ? "#f55f7d" : "#16a7d9";
        let shorts = female ? "#2877a8" : "#f4a63e";
        let accent = female ? "#ffffff" : "#043b56";
        if (outfit.includes("coral")) {
            shirt = "#f55f7d";
            shorts = "#2877a8";
            accent = "#ffffff";
        } else if (outfit.includes("violeta")) {
            shirt = "#8f55ad";
            shorts = "#263a66";
            accent = "#e5b747";
        } else if (outfit.includes("turquesa")) {
            shirt = "#27a19a";
            shorts = "#2877a8";
            accent = "#ffffff";
        } else if (outfit.includes("jaqueta")) {
            shirt = "#263a66";
            shorts = "#2877a8";
            accent = "#e5b747";
        } else if (outfit.includes("sueter")) {
            shirt = "#e7b84a";
            shorts = "#263a66";
            accent = "#263a66";
        }

        let hairColor = "#3a1d13";
        let hairHi = "#7d3b1f";
        if (hair.includes("turquesa") || hair.includes("azul")) {
            hairColor = "#1c566d";
            hairHi = "#4bc4c0";
        } else if (hair.includes("laranja")) {
            hairColor = "#a94c2e";
            hairHi = "#ff9860";
        } else if (hair.includes("preto") || hair.includes("lenco")) {
            hairColor = "#241d25";
            hairHi = "#4a3a43";
        } else if (hair.includes("cacheado")) {
            hairColor = "#4b2418";
            hairHi = "#7d3b1f";
        }

        return { skin, shade, shirt, shorts, accent, hairColor, hairHi, female };
    }

    function avatarHairSvg(parts, colors) {
        const hair = optionName(parts.hair);
        if (hair.includes("careca")) {
            return `<path d="M159 143 C188 111 264 111 293 143" fill="none" stroke="#3a2927" stroke-width="7" stroke-linecap="round" opacity=".28"/>`;
        }
        if (hair.includes("preto longo") || hair.includes("lenco")) {
            const band = hair.includes("lenco")
                ? `<path d="M146 137 C180 88 272 88 306 137 C263 121 189 121 146 137 Z" fill="#8f55ad" stroke="#3a2927" stroke-width="6"/>
                   <circle cx="282" cy="79" r="21" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="6"/>`
                : "";
            return `<path d="M133 143 C137 72 315 72 319 143 L307 310 C268 337 184 337 145 310 Z" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="7"/>
                    <path d="M151 151 C184 101 268 101 301 151 C259 136 193 136 151 151 Z" fill="${colors.hairHi}" opacity=".58"/>
                    ${band}`;
        }
        if (hair.includes("cacheado")) {
            return `<circle cx="145" cy="151" r="31" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="6"/>
                    <circle cx="176" cy="101" r="35" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="6"/>
                    <circle cx="226" cy="82" r="40" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="6"/>
                    <circle cx="278" cy="108" r="35" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="6"/>
                    <circle cx="307" cy="157" r="31" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="6"/>
                    <path d="M151 181 C191 150 265 150 303 181 C259 169 194 169 151 181 Z" fill="#24120d"/>`;
        }
        if (hair.includes("laranja")) {
            return `<path d="M139 154 C148 77 261 54 307 118 C333 154 318 218 288 260 C282 214 261 177 219 166 C189 158 161 174 139 201 Z" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="7"/>
                    <path d="M172 105 C202 76 261 81 294 125 C253 115 205 126 172 158 Z" fill="${colors.hairHi}" opacity=".74"/>`;
        }
        return `<path d="M137 154 C137 90 190 52 254 63 C304 71 327 113 314 165 C284 139 256 126 221 138 C192 148 163 167 139 188 Z" fill="${colors.hairColor}" stroke="#3a2927" stroke-width="7"/>
                <path d="M162 111 C181 146 230 141 268 123 C257 157 210 177 157 178 C148 149 150 127 162 111 Z" fill="#1f100b" opacity=".78"/>
                <path d="M181 79 C171 110 186 133 220 145" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity=".14"/>`;
    }

    function avatarEyesSvg(parts) {
        const eyes = optionName(parts.eyes);
        if (eyes.includes("felizes")) {
            return `<path d="M190 174 C199 165 211 165 220 174" fill="none" stroke="#27212a" stroke-width="8" stroke-linecap="round"/>
                    <path d="M238 174 C247 165 259 165 268 174" fill="none" stroke="#27212a" stroke-width="8" stroke-linecap="round"/>`;
        }
        if (eyes.includes("serenos")) {
            return `<path d="M189 180 H220" stroke="#27212a" stroke-width="7" stroke-linecap="round"/>
                    <path d="M238 180 H269" stroke="#27212a" stroke-width="7" stroke-linecap="round"/>`;
        }
        if (eyes.includes("piscadinha")) {
            return `<circle cx="202" cy="178" r="10" fill="#27212a"/>
                    <circle cx="206" cy="174" r="3" fill="#fff"/>
                    <path d="M238 178 H269" stroke="#27212a" stroke-width="8" stroke-linecap="round"/>`;
        }
        return `<circle cx="202" cy="178" r="11" fill="#27212a"/>
                <circle cx="254" cy="178" r="11" fill="#27212a"/>
                <circle cx="206" cy="174" r="3.5" fill="#fff"/>
                <circle cx="258" cy="174" r="3.5" fill="#fff"/>`;
    }

    function avatarAccessoriesSvg(parts) {
        return parts.accessories
            .map((option) => optionName(option))
            .map((name) => {
                if (name.includes("oculos")) {
                    return `<circle cx="200" cy="180" r="28" fill="#fff" opacity=".12" stroke="#27212a" stroke-width="7"/>
                            <circle cx="256" cy="180" r="28" fill="#fff" opacity=".12" stroke="#27212a" stroke-width="7"/>
                            <path d="M229 180 H227" stroke="#27212a" stroke-width="7" stroke-linecap="round"/>`;
                }
                if (name.includes("brinco")) {
                    return `<circle cx="145" cy="213" r="7" fill="#e5b747" stroke="#3a2927" stroke-width="3"/>
                            <circle cx="311" cy="213" r="7" fill="#e5b747" stroke="#3a2927" stroke-width="3"/>`;
                }
                if (name.includes("fones")) {
                    return `<path d="M149 184 C150 91 306 91 307 184" fill="none" stroke="#263a66" stroke-width="12" stroke-linecap="round"/>
                            <rect x="124" y="166" width="36" height="64" rx="16" fill="#27a19a" stroke="#3a2927" stroke-width="6"/>
                            <rect x="296" y="166" width="36" height="64" rx="16" fill="#27a19a" stroke="#3a2927" stroke-width="6"/>`;
                }
                if (name.includes("gorro")) {
                    return `<path d="M153 94 H303 L228 46 Z" fill="#263a66" stroke="#3a2927" stroke-width="7"/>
                            <rect x="162" y="91" width="132" height="19" rx="9" fill="#e5b747" stroke="#3a2927" stroke-width="5"/>`;
                }
                if (name.includes("livro")) {
                    return `<rect x="332" y="350" width="58" height="86" rx="10" fill="#e5b747" stroke="#3a2927" stroke-width="7"/>
                            <path d="M346 378 H374 M346 398 H368" stroke="#3a2927" stroke-width="6" stroke-linecap="round"/>`;
                }
                return "";
            })
            .join("");
    }

    function legacyAvatarSettings(parts) {
        const base = optionName(parts.base);
        const body = optionName(parts.body);
        const hair = optionName(parts.hair);
        const outfit = optionName(parts.outfit);
        const eyes = optionName(parts.eyes);
        const accessoryNames = parts.accessories.map(optionName);
        const gender = body.includes("feminino") ? "feminino" : "masculino";

        let skin = "#f0c9a2";
        if (base.includes("media")) skin = "#c98259";
        if (base.includes("escura")) skin = "#86543f";
        if (base.includes("quente")) skin = "#b76f4c";
        if (base.includes("dourada")) skin = "#d9a76d";

        let hairColor = "#1c4259";
        let hairStyle = "waves";
        if (hair.includes("turquesa")) {
            hairColor = "#2f8f8b";
            hairStyle = "side";
        } else if (hair.includes("laranja")) {
            hairColor = "#d86f45";
            hairStyle = "waves";
        } else if (hair.includes("cacheado")) {
            hairColor = "#5b3426";
            hairStyle = "curls";
        } else if (hair.includes("preto")) {
            hairColor = "#26314f";
            hairStyle = "waves";
        } else if (hair.includes("castanho")) {
            hairColor = "#8c613b";
            hairStyle = "short";
        } else if (hair.includes("careca")) {
            hairColor = "#bf9663";
            hairStyle = "short";
        } else if (hair.includes("lenco")) {
            hairColor = "#6f4e8c";
            hairStyle = "side";
        }

        let outfitColor = "#1c4259";
        if (outfit.includes("coral")) outfitColor = "#d86f45";
        if (outfit.includes("violeta")) outfitColor = "#6f4e8c";
        if (outfit.includes("turquesa")) outfitColor = "#2f8f8b";
        if (outfit.includes("jaqueta")) outfitColor = "#26314f";
        if (outfit.includes("sueter") || outfit.includes("cachecol")) outfitColor = "#d9b97e";

        let expression = "smile";
        if (eyes.includes("focados")) expression = "focus";
        if (eyes.includes("piscadinha")) expression = "wink";
        if (eyes.includes("serenos")) expression = "focus";

        let accessory = "none";
        if (accessoryNames.some((name) => name.includes("oculos"))) accessory = "round-glasses";
        else if (accessoryNames.some((name) => name.includes("fones"))) accessory = "headphones";
        else if (accessoryNames.some((name) => name.includes("gorro"))) accessory = "cap";
        else if (accessoryNames.some((name) => name.includes("livro"))) accessory = "book";
        else if (accessoryNames.some((name) => name.includes("gravata"))) accessory = "scarf";
        else if (accessoryNames.some((name) => name.includes("brinco"))) accessory = "earrings";

        return {
            skin,
            gender,
            hair: hairColor,
            hairStyle,
            outfit: outfitColor,
            accessory,
            expression,
            backdrop: "library",
        };
    }

    function buildClassicAvatarPreview(parts) {
        const settings = legacyAvatarSettings(parts);
        return `<div
            class="avatar-preview-large avatar-preview-large--classic"
            data-avatar-preview
            data-accessory="${settings.accessory}"
            data-expression="${settings.expression}"
            data-backdrop="${settings.backdrop}"
            data-hair-style="${settings.hairStyle}"
            data-gender="${settings.gender}"
            style="--avatar-skin: ${settings.skin}; --avatar-hair: ${settings.hair}; --avatar-outfit: ${settings.outfit};"
        >
            <span class="avatar-backdrop"></span>
            <span class="avatar-shadow"></span>
            <span class="avatar-body"></span>
            <span class="avatar-neck"></span>
            <span class="avatar-ear left"></span>
            <span class="avatar-ear right"></span>
            <span class="avatar-head"></span>
            <span class="avatar-hair"></span>
            <span class="avatar-bang"></span>
            <span class="avatar-brow left"></span>
            <span class="avatar-brow right"></span>
            <span class="avatar-eye left"></span>
            <span class="avatar-eye right"></span>
            <span class="avatar-smile"></span>
            <span class="avatar-accessory avatar-accessory--glasses"></span>
            <span class="avatar-accessory avatar-accessory--round-glasses"></span>
            <span class="avatar-accessory avatar-accessory--headphones"></span>
            <span class="avatar-accessory avatar-accessory--cap"></span>
            <span class="avatar-accessory avatar-accessory--crown"></span>
            <span class="avatar-accessory avatar-accessory--scarf"></span>
            <span class="avatar-accessory avatar-accessory--backpack"></span>
            <span class="avatar-accessory avatar-accessory--book"></span>
            <span class="avatar-accessory avatar-accessory--earrings"></span>
            <span class="avatar-accessory avatar-accessory--sparkle"></span>
        </div>`;
    }

    function buildPresetAvatarIllustration(parts) {
        const colors = avatarPalette(parts);
        const bodyName = optionName(parts.body);
        const hairName = optionName(parts.hair);
        const accessoryNames = parts.accessories.map(optionName);
        const female = bodyName.includes("feminino");
        const skin = colors.skin;
        const shade = colors.shade;
        const shirt = female ? "#f65f7f" : "#18a8d8";
        const shorts = female ? "#2b7fa9" : "#f2ad3e";
        const shoe = "#293f60";
        const hair = female ? "#2b222b" : "#3a1d13";
        const hairLight = female ? "#4c3d48" : "#7a3a20";
        const showGlasses = accessoryNames.some((name) => name.includes("oculos"));
        const showEarrings = female || accessoryNames.some((name) => name.includes("brinco"));
        const showHeadphones = accessoryNames.some((name) => name.includes("fones"));
        const smile = `<path d="M204 230 C219 244 243 244 258 230" fill="none" stroke="#27212a" stroke-width="7" stroke-linecap="round"/>`;
        const eyes = showGlasses
            ? `<circle cx="202" cy="178" r="25" fill="#fff" opacity=".12" stroke="#27212a" stroke-width="7"/>
               <circle cx="260" cy="178" r="25" fill="#fff" opacity=".12" stroke="#27212a" stroke-width="7"/>
               <path d="M228 178 H234" stroke="#27212a" stroke-width="7" stroke-linecap="round"/>
               <circle cx="202" cy="178" r="7" fill="#27212a"/>
               <circle cx="260" cy="178" r="7" fill="#27212a"/>`
            : `<circle cx="203" cy="178" r="10" fill="#27212a"/>
               <circle cx="259" cy="178" r="10" fill="#27212a"/>
               <circle cx="207" cy="174" r="3" fill="#fff"/>
               <circle cx="263" cy="174" r="3" fill="#fff"/>`;
        const hairShape = female
            ? `<path d="M142 147 C146 76 314 76 318 147 L306 314 C271 342 189 342 154 314 Z" fill="${hair}" stroke="#3a2927" stroke-width="7"/>
               <path d="M158 146 C190 98 270 98 302 146 C262 132 198 132 158 146 Z" fill="${hairLight}"/>
               <path d="M174 121 C205 139 248 139 283 121" fill="none" stroke="#f65f7f" stroke-width="8" stroke-linecap="round"/>`
            : hairName.includes("cacheado")
              ? `<circle cx="151" cy="151" r="30" fill="${hair}" stroke="#3a2927" stroke-width="6"/>
                 <circle cx="185" cy="102" r="34" fill="${hair}" stroke="#3a2927" stroke-width="6"/>
                 <circle cx="228" cy="86" r="39" fill="${hair}" stroke="#3a2927" stroke-width="6"/>
                 <circle cx="273" cy="107" r="34" fill="${hair}" stroke="#3a2927" stroke-width="6"/>
                 <circle cx="303" cy="153" r="30" fill="${hair}" stroke="#3a2927" stroke-width="6"/>
                 <path d="M154 180 C192 152 264 152 302 180 Z" fill="#1e100c"/>`
              : `<path d="M141 154 C144 92 195 55 256 64 C307 72 331 115 315 166 C286 139 258 128 223 140 C193 150 165 169 141 192 Z" fill="${hair}" stroke="#3a2927" stroke-width="7"/>
                 <path d="M166 111 C184 148 233 144 272 126 C259 160 213 178 160 180 C151 149 153 128 166 111 Z" fill="#20110b"/>
                 <path d="M184 82 C175 111 190 134 223 146" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity=".14"/>`;
        const torso = female
            ? `M159 314 C182 294 278 294 301 314 L322 407 C294 426 166 426 138 407 Z`
            : `M151 314 C176 292 284 292 309 314 L333 406 C300 428 160 428 127 406 Z`;
        const bottoms = female
            ? `M166 418 H294 L306 493 C282 507 256 501 230 488 C204 501 178 507 154 493 Z`
            : `M159 419 H301 L314 497 C288 512 258 505 230 490 C202 505 172 512 146 497 Z`;

        return `<svg viewBox="0 0 460 620" role="img" aria-label="Avatar Lecto" class="avatar-final-svg">
            <defs>
                <radialGradient id="presetSkin" cx="35%" cy="20%" r="82%">
                    <stop offset="0" stop-color="#fff" stop-opacity=".6"/>
                    <stop offset=".38" stop-color="${skin}"/>
                    <stop offset="1" stop-color="${shade}" stop-opacity=".55"/>
                </radialGradient>
                <filter id="presetShadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="8" stdDeviation="7" flood-color="#1c4259" flood-opacity=".16"/>
                </filter>
            </defs>
            <g filter="url(#presetShadow)">
                <ellipse cx="230" cy="586" rx="120" ry="18" fill="#173245" opacity=".14"/>
                <path d="M188 406 C181 467 177 525 170 584" fill="none" stroke="${skin}" stroke-width="30" stroke-linecap="round"/>
                <path d="M272 406 C279 467 283 525 290 584" fill="none" stroke="${skin}" stroke-width="30" stroke-linecap="round"/>
                <path d="M160 584 C185 573 218 576 226 598 C197 610 158 610 136 599 C136 592 144 587 160 584 Z" fill="#fffdf7" stroke="#3a2927" stroke-width="6"/>
                <path d="M300 584 C275 573 242 576 234 598 C263 610 302 610 324 599 C324 592 316 587 300 584 Z" fill="#fffdf7" stroke="#3a2927" stroke-width="6"/>
                <path d="M152 601 H226" stroke="${shoe}" stroke-width="11" stroke-linecap="round"/>
                <path d="M234 601 H308" stroke="${shoe}" stroke-width="11" stroke-linecap="round"/>
                <path d="M173 340 C135 374 115 420 106 476" fill="none" stroke="${skin}" stroke-width="27" stroke-linecap="round"/>
                <path d="M287 340 C325 374 345 420 354 476" fill="none" stroke="${skin}" stroke-width="27" stroke-linecap="round"/>
                <circle cx="105" cy="480" r="18" fill="${skin}" stroke="#3a2927" stroke-width="6"/>
                <circle cx="355" cy="480" r="18" fill="${skin}" stroke="#3a2927" stroke-width="6"/>
                <path d="M202 256 H258 L268 326 C248 341 212 341 192 326 Z" fill="${skin}" stroke="#3a2927" stroke-width="6"/>
                <ellipse cx="147" cy="179" rx="20" ry="27" fill="${skin}" stroke="#3a2927" stroke-width="6"/>
                <ellipse cx="313" cy="179" rx="20" ry="27" fill="${skin}" stroke="#3a2927" stroke-width="6"/>
                <ellipse cx="230" cy="174" rx="84" ry="96" fill="url(#presetSkin)" stroke="#3a2927" stroke-width="7"/>
                ${hairShape}
                ${showHeadphones ? `<path d="M151 184 C152 92 308 92 309 184" fill="none" stroke="#263a66" stroke-width="12" stroke-linecap="round"/><rect x="126" y="166" width="36" height="64" rx="16" fill="#27a19a" stroke="#3a2927" stroke-width="6"/><rect x="298" y="166" width="36" height="64" rx="16" fill="#27a19a" stroke="#3a2927" stroke-width="6"/>` : ""}
                ${showEarrings ? `<circle cx="146" cy="215" r="7" fill="#e5b747" stroke="#3a2927" stroke-width="3"/><circle cx="314" cy="215" r="7" fill="#e5b747" stroke="#3a2927" stroke-width="3"/>` : ""}
                <ellipse cx="196" cy="212" rx="17" ry="9" fill="#eb6f74" opacity=".16"/>
                <ellipse cx="264" cy="212" rx="17" ry="9" fill="#eb6f74" opacity=".16"/>
                <path d="M230 180 C222 204 224 217 236 223" fill="none" stroke="${shade}" stroke-width="5" stroke-linecap="round" opacity=".34"/>
                ${eyes}
                ${smile}
                <path d="${torso}" fill="${shirt}" stroke="#3a2927" stroke-width="7" stroke-linejoin="round"/>
                <path d="M171 315 L129 365 L153 389 L191 340" fill="${shirt}" stroke="#3a2927" stroke-width="7"/>
                <path d="M289 315 L331 365 L307 389 L269 340" fill="${shirt}" stroke="#3a2927" stroke-width="7"/>
                <path d="M204 314 L230 342 L256 314" fill="none" stroke="${female ? "#fff" : "#0b4d73"}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="${bottoms}" fill="${shorts}" stroke="#3a2927" stroke-width="7" stroke-linejoin="round"/>
                <path d="M230 432 V493" stroke="#3a2927" stroke-width="5" stroke-linecap="round" opacity=".35"/>
            </g>
        </svg>`;
    }

    function buildAvatarIllustration(parts) {
        return buildClassicAvatarPreview(parts);
        const c = avatarPalette(parts);
        const torso = c.female
            ? `M158 308 C177 286 279 286 298 308 L321 402 C292 421 164 421 135 402 Z`
            : `M151 310 C174 287 282 287 305 310 L330 402 C298 422 158 422 126 402 Z`;
        const shorts = c.female
            ? `M166 415 H290 L305 494 C280 507 253 501 228 487 C203 501 176 507 151 494 Z`
            : `M160 416 H296 L312 498 C286 512 257 505 228 490 C199 505 170 512 144 498 Z`;

        return `<svg viewBox="0 0 456 620" role="img" aria-label="Avatar Lecto" class="avatar-final-svg">
            <defs>
                <radialGradient id="finalSkin" cx="35%" cy="20%" r="82%">
                    <stop offset="0" stop-color="#fff" stop-opacity=".58"/>
                    <stop offset=".36" stop-color="${c.skin}"/>
                    <stop offset="1" stop-color="${c.shade}" stop-opacity=".55"/>
                </radialGradient>
                <filter id="finalShadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="8" stdDeviation="7" flood-color="#1c4259" flood-opacity=".18"/>
                </filter>
            </defs>
            <g filter="url(#finalShadow)">
                <ellipse cx="228" cy="586" rx="124" ry="18" fill="#173245" opacity=".14"/>
                <path d="M185 405 C178 466 174 524 167 584" fill="none" stroke="${c.skin}" stroke-width="30" stroke-linecap="round"/>
                <path d="M271 405 C278 466 282 524 289 584" fill="none" stroke="${c.skin}" stroke-width="30" stroke-linecap="round"/>
                <path d="M157 584 C182 572 216 575 225 598 C196 610 156 610 133 599 C133 592 141 587 157 584 Z" fill="#fffdf7" stroke="#3a2927" stroke-width="6"/>
                <path d="M299 584 C274 572 240 575 231 598 C260 610 300 610 323 599 C323 592 315 587 299 584 Z" fill="#fffdf7" stroke="#3a2927" stroke-width="6"/>
                <path d="M149 601 H225" stroke="#304563" stroke-width="11" stroke-linecap="round"/>
                <path d="M231 601 H307" stroke="#304563" stroke-width="11" stroke-linecap="round"/>
                <path d="M171 335 C133 366 112 410 103 474" fill="none" stroke="${c.skin}" stroke-width="28" stroke-linecap="round"/>
                <path d="M285 335 C323 366 344 410 353 474" fill="none" stroke="${c.skin}" stroke-width="28" stroke-linecap="round"/>
                <circle cx="102" cy="478" r="18" fill="${c.skin}" stroke="#3a2927" stroke-width="6"/>
                <circle cx="354" cy="478" r="18" fill="${c.skin}" stroke="#3a2927" stroke-width="6"/>
                <path d="M200 256 H256 L266 325 C246 340 210 340 190 325 Z" fill="${c.skin}" stroke="#3a2927" stroke-width="6"/>
                <ellipse cx="145" cy="178" rx="20" ry="27" fill="${c.skin}" stroke="#3a2927" stroke-width="6"/>
                <ellipse cx="311" cy="178" rx="20" ry="27" fill="${c.skin}" stroke="#3a2927" stroke-width="6"/>
                <ellipse cx="228" cy="174" rx="84" ry="96" fill="url(#finalSkin)" stroke="#3a2927" stroke-width="7"/>
                ${avatarHairSvg(parts, c)}
                <ellipse cx="194" cy="212" rx="18" ry="9" fill="#eb6f74" opacity=".18"/>
                <ellipse cx="262" cy="212" rx="18" ry="9" fill="#eb6f74" opacity=".18"/>
                <path d="M228 180 C220 203 222 217 234 223" fill="none" stroke="${c.shade}" stroke-width="5" stroke-linecap="round" opacity=".34"/>
                ${avatarEyesSvg(parts)}
                <path d="M198 231 C215 248 241 248 258 231" fill="none" stroke="#27212a" stroke-width="8" stroke-linecap="round"/>
                <path d="${torso}" fill="${c.shirt}" stroke="#3a2927" stroke-width="7" stroke-linejoin="round"/>
                <path d="M169 311 L126 363 L151 386 L190 338" fill="${c.shirt}" stroke="#3a2927" stroke-width="7"/>
                <path d="M287 311 L330 363 L305 386 L266 338" fill="${c.shirt}" stroke="#3a2927" stroke-width="7"/>
                <path d="M202 310 L228 338 L254 310" fill="none" stroke="${c.accent}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="${shorts}" fill="${c.shorts}" stroke="#3a2927" stroke-width="7" stroke-linejoin="round"/>
                <path d="M228 431 V493" stroke="#3a2927" stroke-width="5" stroke-linecap="round" opacity=".35"/>
                ${avatarAccessoriesSvg(parts)}
            </g>
        </svg>`;
    }

    function renderLayeredAvatar(profile) {
        const builder = document.querySelector("[data-avatar-builder]");
        if (!builder) return;

        const canvas = builder.querySelector("[data-avatar-layer-canvas]");
        if (!canvas) return;

        ensureAvatarLayerDefaults(builder, profile);
        const options = getAvatarOptions(builder);
        const byId = new Map(options.map((option) => [option.id, option]));
        const selectedIds = [
            profile.avatarLayers.base_body,
            profile.avatarLayers.body_style,
            profile.avatarLayers.hair_style,
            profile.avatarLayers.outfit,
            profile.avatarLayers.eyes,
            ...(profile.avatarLayers.accessories || []),
        ].filter(Boolean);
        const parts = selectedAvatarParts(profile, byId);
        canvas.replaceChildren();
        canvas.insertAdjacentHTML("afterbegin", buildAvatarIllustration(parts));

        options.forEach((option) => {
            const selected = selectedIds.includes(option.id);
            const unlocked = isAvatarOptionUnlocked(profile, option);
            option.node.classList.toggle("is-selected", selected);
            option.node.classList.toggle("is-locked", !unlocked);
            option.node.classList.toggle("is-unavailable", !unlocked && !option.canUnlock);
            option.node.disabled = !unlocked && !option.canUnlock;
            const state = option.node.querySelector("[data-option-state]");
            if (state) {
                if (selected) {
                    state.textContent = "Selecionado";
                } else if (!unlocked && option.readsMissing > 0) {
                    state.textContent = `Indisponivel: faltam ${option.readsMissing} leitura(s)`;
                } else if (!unlocked && option.coinsMissing > 0) {
                    state.textContent = `Indisponivel: faltam ${option.coinsMissing} moedas`;
                } else if (!unlocked) {
                    state.textContent = `Liberar ${option.price}`;
                } else {
                    state.textContent = "Selecionar";
                }
            }
        });
    }

    function setupBot() {
        const root = document.querySelector("[data-lecto-bot]");
        if (!root) return;

        const panel = root.querySelector("[data-bot-panel]");
        const answer = root.querySelector("[data-bot-answer]");
        const answers = {
            nivel: "Comece pelo quiz de nivelamento. Se acertar 5 de 7, esse nivel provavelmente combina com voce.",
            pontos: "Voce ganha 5 moedinhas ao marcar um texto como lido e pontos extras ao responder o quiz do texto.",
            avatar: "Abra Meu Avatar no menu, escolha nome, cenario e aderecos. Tudo fica salvo neste navegador.",
            quiz: "O quiz de texto tem 5 perguntas. Leia com calma e use as palavras destacadas para revisar.",
        };

        root.querySelector("[data-bot-toggle]").addEventListener("click", () => {
            panel.hidden = !panel.hidden;
        });

        root.querySelector("[data-bot-close]").addEventListener("click", () => {
            panel.hidden = true;
        });

        root.querySelectorAll("[data-bot-question]").forEach((button) => {
            button.addEventListener("click", () => {
                answer.textContent = answers[button.dataset.botQuestion] || "Ainda estou aprendendo essa resposta.";
            });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        renderProfile(loadProfile());
        setupReadingPoints();
        setupFavoriteButtons();
        setupQuizReward();
        setupAvatarPage();
        setupBot();
    });
})();
