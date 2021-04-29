import axios from "axios";

const http = axios.create({
  baseURL: "http://localhost:8888",
  headers: {
    "Content-type": "application/json",
  },
});

class UploadFilesService {
  upload(file: File, onUploadProgress: (progressEvent: any) => void) {
    let formData = new FormData();

    formData.append("file", file);

    return http.post("/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
  }

  getFiles() {
    return http.get("/files");
  }
}

export default new UploadFilesService();
