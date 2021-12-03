from .base import ReboticsBaseProvider, remote_service


class HawkeyeProvider(ReboticsBaseProvider):

    @remote_service('/api/camera/heartbeats/')
    def save_camera_heartbeat(self, shelf_camera, battery_status, free_storage, used_storage):
        return self.session.post(json={
            "shelf_camera": shelf_camera,
            "battery_status": battery_status,
            "free_storage": free_storage,
            "used_storage": used_storage
        })

    @remote_service('/api/camera/camera-actions/')
    def save_camera_action(self, action_type, status_type, payload, shelf_camera):
        return self.session.post(json={
            "action_type": action_type,
            "status_type": status_type,
            "payload": payload,
            "shelf_camera": shelf_camera
        })

    @remote_service('/api/camera/camera-actions/')
    def get_camera_actions(self):
        return self.session.get()

    @remote_service('/api/camera/retailer/')
    def save_retailer(self, codename, token):
        return self.session.post(json={
            "retailer": codename,
            "token": token
        })

    @remote_service('/api/camera/fixtures/')
    def save_fixture(self, retailer, store_id, aisle, section):
        return self.session.post(
            json={
                "store_id": store_id,
                "aisle": aisle,
                "section": section,
                "retailer": retailer
            }
        )

    @remote_service('/api/camera/fixtures/{id}')
    def delete_fixture(self, pk):
        return self.session.delete(id=pk)

    @remote_service('/api/camera/fixtures/')
    def get_fixtures(self):
        return self.session.get()

    @remote_service('/api/camera/shelf-cameras/')
    def save_shelf_camera(self, camera_id, added_by, fixture):
        return self.session.post(json={
            "camera_id": camera_id,
            "added_by": added_by,
            "fixture": fixture
        })

    @remote_service('/api/camera/shelf-cameras/')
    def get_shelf_cameras(self):
        return self.send_post()

    @remote_service('/api/fetcher/{camera_id}/')
    def save_capture(self, camera, file_key, bucket_name):
        return self.session.post(
            camera_id=camera,
            json={
                "file_key": file_key,
                "bucket_name": bucket_name
            })
