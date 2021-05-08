import axios from "axios";

const http = axios.create({
  // baseURL: "/",
  headers: {
    "Content-type": "application/json",
  },
});

class UploadFilesService {
  upload(
    url: string,
    data: Object,
    onUploadProgress: (progressEvent: any) => void,
    token: string
  ) {
    let formData = new FormData();

    Object.keys(data).forEach((k) => {
      // @ts-ignore
      formData.append(k, data[k]);
    });

    return http.post(url || "/api/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
      onUploadProgress,
    });
  }

  getFiles() {
    return http.get("/files");
  }
}

export default new UploadFilesService();
