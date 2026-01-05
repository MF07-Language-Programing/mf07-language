# Demonstração prática do runtime de IA da CorpLang com o Basic Kit embutido

print("=== Demo: CorpLang AI Runtime ===");

# Carrega dataset simulado e inspeciona os registros disponíveis
var dataset_result = dataset load customers("customers.csv");
print("Dataset carregado:", JSON.stringify(dataset_result));

# Lista datasets conhecidos pelo modelo de crédito
var dataset_listing = model datasets credit;
print("Datasets registrados para o modelo de crédito:", JSON.stringify(dataset_listing));

# Cria e prepara o modelo, incluindo contrato de resposta e função de bootstrap
var creation_report = model create credit (type = "classifier", version = "1.0.0");
print("Estado do modelo após criação:", JSON.stringify(creation_report));

model response credit CreditScorePayload;
model initFunction credit bootstrapCreditModel;

# Executa treinamento utilizando o dataset carregado
var training_report = model train credit (dataset = "customers", target_accuracy = 0.92);
print("Relatório de treinamento:", JSON.stringify(training_report));

# Realiza uma inferência e exibe a resposta detalhada (inclui backend do Basic Kit)
var prediction = model predict credit (
    input = {
        "customerId": 1024,
        "income": 7800,
        "score": 650,
        "history": ["on_time", "late", "on_time"]
    }
);
print("Resposta de predição:", JSON.stringify(prediction));

# Envia uma requisição contextual que ativa o pipeline de IA local (Basic Kit)
var request_result = model request credit {
    "prompt": "Gerar resumo em linguagem natural para o cliente 1024",
    "locale": "pt-BR",
    "metadata": {
        "canal": "app",
        "operador": "analista_risco"
    }
} response CreditNarrative;
print("Resposta da requisição contextual:", JSON.stringify(request_result));

# Demonstração direta do Basic Kit automático (sem configuração externa de IA)
print("--- Basic Kit embutido ---");
var basic_prediction = model predict basicKit (
    input = {
        "texto": "Cliente 1024 apresenta melhora no comportamento de pagamento",
        "sentimento": "positivo"
    }
);
print("Predição via Basic Kit:", JSON.stringify(basic_prediction));

var basic_request = model request basicKit {
    "prompt": "Resumir evidências do cliente 1024 para o comitê interno",
    "canal": "backoffice"
};
print("Resposta do Basic Kit:", JSON.stringify(basic_request));
