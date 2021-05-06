import axios from "axios";

const http = axios.create({
  baseURL: "http://localhost:8888",
  headers: {
    "Content-type": "application/json",
  },
});

class UploadFilesService {
  upload(
    url: string,
    data: Object,
    onUploadProgress: (progressEvent: any) => void
  ) {
    let formData = new FormData();

    Object.keys(data).forEach((k) => {
      // @ts-ignore
      formData.append(k, data[k]);
    });

    return http.post(url || "/upload/", formData, {
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
