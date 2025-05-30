resource "yandex_compute_instance" "vm-1" {
  allow_stopping_for_update = true
  name                      = "redis"
  platform_id               = "standard-v3"
  zone                      = "ru-central1-b"
  resources {
    cores         = "2"
    memory        = "4"
    core_fraction = "100"
  }

  boot_disk {
    initialize_params {
      image_id = "fd8chrq89mmk8tqm85r8"
      size     = "20"
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id = "e2lpg52vf357d83h50p3"
    nat       = true
  }

  metadata = {
    user-data          = "${file("cloud-init_mail.yaml")}"
    serial-port-enable = "1"
  }
}
