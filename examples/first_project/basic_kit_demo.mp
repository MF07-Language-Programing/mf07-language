# Demonstração enxuta do Basic Kit utilizando scikit-learn (quando disponível)

print("=== Basic Kit (scikit-learn) - Demo Enxuta ===");


# Predição direta (exemplo de entrada)
var resultado_predicao = model predict baseKit (
    input = {
        "texto": "Uma fraude foi detectada em uma transação suspeita",
        "flags": ["investigacao", "risco"]
    }
);


print("\n======== PREDIÇÃO RÁPIDA ========");
print("Backend:", resultado_predicao.backend);
var label = resultado_predicao.prediction.label;
var conf = resultado_predicao.confidence;
var friendly_label = (label == "risk") ? "RISK" : ((label == "safe") ? "SAFE" : label);
print("Classificação:", friendly_label, " (raw:", label, ")");
print("Confiança:", (conf != null) ? conf : "-");

# Imprime probabilidades com espaçamento alinhado
var dist = resultado_predicao.prediction.probabilities;
if (dist != null) {
    print("Probabilidades:");
    print("  attention: ", (dist.attention != null) ? dist.attention : "-");
    print("  risk:      ", (dist.risk != null) ? dist.risk : "-");
    print("  safe:      ", (dist.safe != null) ? dist.safe : "-");
} else {
    print("Probabilidades: (não disponíveis)");
}

# Resumo amigável
if (label == "risk") {
    print("\n>>> AÇÃO: RISCO detectado. Recomenda-se: revisar, sinalizar e escalonar.");
} else if (label == "safe") {
    print("\n>>> AÇÃO: Conteúdo considerado SEGURO.");
} else {
    print("\n>>> AÇÃO: Classificação:", friendly_label);
}

# Requisição contextual (exemplo)
var response_bk = model request basicKit {
    "prompt": "Nenhum problema encontrada nas emissões de notas. Tudo parece estar em ordem.",
    "contexto": {
        "segmento": "corporativo",
        "prioridade": "alta"
    }
};

print("\n======== REQUISIÇÃO CONTEXTUAL ========");
print("Backend:", response_bk.backend);
print("Classificação final:", response_bk.classification);
print("Confiança:", (response_bk.confidence != null) ? response_bk.confidence : "-");

var dist_req = response_bk.probabilities;
if (dist_req != null) {
    print("Probabilidades:");
    print("  attention: ", (dist_req.attention != null) ? dist_req.attention : "-");
    print("  risk:      ", (dist_req.risk != null) ? dist_req.risk : "-");
    print("  safe:      ", (dist_req.safe != null) ? dist_req.safe : "-");
} else {
    print("Probabilidades: (não disponíveis)");
}

if (response_bk.preview != null) {
    print("\n[Preview]");
    print("  \"" + response_bk.preview + "\"");
}

print("\n--- Fim da demonstração ---");