import axios from "axios";
import { config } from "../../utils/config";

const backendInstance = axios.create({
  baseURL: config.apiUrl,
});

export default backendInstance;
