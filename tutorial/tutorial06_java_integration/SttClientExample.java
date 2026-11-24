package com.example.stt.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

/**
 * Tutorial 06: Java Spring Boot 轉發音檔至 Python FastAPI 語音辨識微服務範例
 * 架構說明：
 * 前端網頁 (Java 提供) -> POST /java/api/stt -> Java RestClient -> POST http://127.0.0
 */
@RestController
@RequestMapping("/java/api/stt")
public class SttClientExample {

    @Value("${python.stt.url:http://127.0.0}")
    private String pythonSttUrl;

    private final RestClient restClient = RestClient.create();

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> forwardToWhisper(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "vad_filter", defaultValue = "true") boolean vadFilter,
            @RequestParam(value = "min_silence_duration_ms", defaultValue = "500") int minSilenceMs,
            @RequestParam(value = "threshold", defaultValue = "0.5") double threshold
    ) throws IOException {

        // 1. 將 MultipartFile 包裝為具備檔名的 ByteArrayResource (FastAPI 依賴檔名判斷副檔名)
        String originalFilename = file.getOriginalFilename() != null ? file.getOriginalFilename() : "recording.webm";
        ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return originalFilename;
            }
        };

        // 2. 組裝 multipart/form-data 表單資料
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", fileResource);
        body.add("vad_filter", String.valueOf(vadFilter));
        body.add("min_silence_duration_ms", String.valueOf(minSilenceMs));
        body.add("threshold", String.valueOf(threshold));

        // 3. 發送 POST 請求至 Python FastAPI 微服務並直接回傳 JSON 結果
        Map response = restClient.post()
                .uri(pythonSttUrl)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(body)
                .retrieve()
                .body(Map.class);

        return ResponseEntity.ok(response);
    }
}
